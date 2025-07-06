"""
RAG Processor Module

This module handles the Retrieval-Augmented Generation (RAG) pipeline:
- Query processing
- Embedding generation
- Document retrieval
- Response generation using Ollama
"""

import ollama
from config import config
from chromadb_manager import ChromaDBManager


class RAGProcessor:
    """Handles RAG (Retrieval-Augmented Generation) operations."""
    
    def __init__(self, chromadb_manager: ChromaDBManager, 
                 embedding_model: str = None, generation_model: str = None):
        """
        Initialize RAG processor.
        
        Args:
            chromadb_manager (ChromaDBManager): ChromaDB manager instance
            embedding_model (str): Ollama model for embeddings. Uses config default if None.
            generation_model (str): Ollama model for generation. Uses config default if None.
        """
        self.chromadb_manager = chromadb_manager
        self.embedding_model = embedding_model or config.EMBEDDING_MODEL
        self.generation_model = generation_model or config.GENERATION_MODEL
    
    def generate_embedding(self, text: str) -> dict:
        """
        Generate embedding for the given text using Ollama.
        
        Args:
            text (str): Text to generate embedding for
            
        Returns:
            dict: Ollama embedding response or error dict
        """
        try:
            if config.VERBOSE_LOGGING:
                print(f"Generating embedding for text using '{self.embedding_model}'...")
            
            response = ollama.embed(
                model=self.embedding_model,
                input=text
            )
            return response
            
        except ollama.ResponseError as e:
            return {
                "error": f"Ollama embedding error: {e}",
                "suggestion": f"Please ensure Ollama server is running and model '{self.embedding_model}' is pulled."
            }
        except Exception as e:
            return {"error": f"Unexpected error generating embedding: {e}"}
    
    def retrieve_relevant_documents(self, query_text: str, n_results: int = None) -> dict:
        """
        Retrieve relevant documents from ChromaDB using dynamic distance filtering.
        
        Args:
            query_text (str): Text query to search for
            n_results (int): Number of results to return. Uses config default if None.
            
        Returns:
            dict: Retrieved documents and metadata with filtering information
        """
        try:
            if config.VERBOSE_LOGGING:
                print("Querying ChromaDB for relevant documents with dynamic filtering...")
            
            # Use dynamic distance filtering for improved accuracy
            results = self.chromadb_manager.query_with_dynamic_distance_filter(
                query_text, n_results
            )
            
            if "error" in results:
                return results
            
            # Process and limit retrieved data
            retrieved_data = "No relevant information found."
            filtering_info = results.get('filtering_info', {})
            
            # Check if results were rejected by hard distance threshold
            if filtering_info.get('rejected_by_hard_threshold'):
                retrieved_data = "No relevant information found."
                if config.VERBOSE_LOGGING:
                    print(f"All results rejected by hard distance threshold ({config.HARD_DISTANCE_THRESHOLD})")
                    print(f"Best available distance was: {filtering_info.get('best_distance', 'N/A'):.4f}")
            elif results and results.get('documents') and results['documents'][0]:
                documents = results['documents'][0]
                distances = results.get('distances', [[]])[0]
                
                # Combine multiple documents if available
                combined_docs = []
                total_length = 0
                max_length = config.MAX_RETRIEVED_DATA_LENGTH
                
                for i, doc in enumerate(documents):
                    if total_length + len(doc) <= max_length:
                        doc_with_score = doc
                        if distances and i < len(distances) and config.DISTANCE_DEBUG_MODE:
                            doc_with_score = f"[Score: {distances[i]:.3f}] {doc}"
                        combined_docs.append(doc_with_score)
                        total_length += len(doc)
                    else:
                        # Add partial document if there's meaningful space
                        remaining_space = max_length - total_length
                        if remaining_space > 100:
                            partial_doc = doc[:remaining_space] + "..."
                            if distances and i < len(distances) and config.DISTANCE_DEBUG_MODE:
                                partial_doc = f"[Score: {distances[i]:.3f}] {partial_doc}"
                            combined_docs.append(partial_doc)
                        break
                
                retrieved_data = "\n\n".join(combined_docs) if combined_docs else "No relevant information found."
                
                if config.VERBOSE_LOGGING:
                    print(f"Retrieved {len(combined_docs)} document(s)")
                    if filtering_info.get('filtering_enabled'):
                        print(f"Filtering: {filtering_info.get('original_count', 0)} → {filtering_info.get('filtered_count', 0)} results")
                        if filtering_info.get('best_distance') is not None:
                            print(f"Best match distance: {filtering_info['best_distance']:.4f}")
                    print(f"Data snippet: '{retrieved_data[:100]}...'")
            else:
                if config.VERBOSE_LOGGING:
                    print("No relevant documents found in the collection for this query.")
            
            return {
                "retrieved_data": retrieved_data,
                "raw_results": results,
                "filtering_info": filtering_info,
                "distances": results.get('distances', [[]])[0] if results.get('distances') else []
            }
            
        except Exception as e:
            return {"error": f"Error retrieving documents: {e}"}
    
    def retrieve_relevant_documents_legacy(self, query_embeddings: list, n_results: int = None) -> dict:
        """
        Legacy method: Retrieve relevant documents from ChromaDB using query embeddings.
        Kept for backward compatibility.
        
        Args:
            query_embeddings (list): Embeddings to query with
            n_results (int): Number of results to return. Uses config default if None.
            
        Returns:
            dict: Retrieved documents and metadata
        """
        try:
            if config.VERBOSE_LOGGING:
                print("Querying ChromaDB for relevant documents (legacy method)...")
            
            results = self.chromadb_manager.query_collection(query_embeddings, n_results)
            
            if "error" in results:
                return results
            
            # Process and limit retrieved data
            retrieved_data = "No relevant information found."
            if results and results.get('documents') and results['documents'][0]:
                data = results['documents'][0][0]
                # Limit the retrieved data to avoid excessively long prompts
                max_length = config.MAX_RETRIEVED_DATA_LENGTH
                retrieved_data = data if len(data) < max_length else data[:max_length] + "..."
                
                if config.VERBOSE_LOGGING:
                    print(f"Retrieved data snippet: '{retrieved_data[:100]}...'")
            else:
                if config.VERBOSE_LOGGING:
                    print("No relevant documents found in the collection for this query.")
            
            return {
                "retrieved_data": retrieved_data,
                "raw_results": results
            }
            
        except Exception as e:
            return {"error": f"Error retrieving documents: {e}"}
    
    def generate_response(self, prompt: str, context_data: str = "") -> dict:
        """
        Generate response using Ollama with optional context data.
        
        Args:
            prompt (str): User prompt/query
            context_data (str): Retrieved context data to include
            
        Returns:
            dict: Generated response or error dict
        """
        try:
            if config.VERBOSE_LOGGING:
                print(f"Generating response using '{self.generation_model}'...")
            
            # Construct full prompt with context
            if context_data and context_data != "No relevant information found.":
                full_prompt = f"Using this data: {context_data}. Respond to this prompt: {prompt}"
            else:
                full_prompt = prompt
            
            output = ollama.generate(
                model=self.generation_model,
                prompt=full_prompt
            )
            
            response_text = output.get('response', 'No response generated.')
            return {
                "response": response_text,
                "full_prompt": full_prompt if config.DEBUG_MODE else None
            }
            
        except ollama.ResponseError as e:
            return {
                "error": f"Ollama generation error: {e}",
                "suggestion": f"Please ensure Ollama server is running and model '{self.generation_model}' is pulled."
            }
        except Exception as e:
            return {"error": f"Unexpected error generating response: {e}"}
    
    def process_query(self, query_prompt: str) -> str:
        """
        Process a complete RAG query from start to finish with dynamic distance filtering.
        
        Args:
            query_prompt (str): The user's query
            
        Returns:
            str: The final response or error message
        """
        try:
            if not query_prompt.strip():
                return "Please enter a non-empty query."
            
            if config.VERBOSE_LOGGING:
                print(f"\n--- Processing Query: '{query_prompt}' ---")
            
            # Use direct text-based retrieval with dynamic filtering
            retrieval_result = self.retrieve_relevant_documents(query_prompt)
            if "error" in retrieval_result:
                return f"Error: {retrieval_result['error']}"
            
            # Generate response with context
            generation_result = self.generate_response(
                query_prompt, 
                retrieval_result["retrieved_data"]
            )
            if "error" in generation_result:
                return f"Error: {generation_result['error']}\n{generation_result.get('suggestion', '')}"
            
            # Add filtering information to response if in debug mode
            response = generation_result["response"]
            if config.DISTANCE_DEBUG_MODE and retrieval_result.get('filtering_info'):
                filtering_info = retrieval_result['filtering_info']
                if filtering_info.get('rejected_by_hard_threshold'):
                    debug_info = f"\n\n[Debug] Hard threshold rejection: {filtering_info.get('best_distance', 'N/A'):.4f} > {filtering_info.get('hard_threshold_value', 'N/A')}"
                elif filtering_info.get('filtering_enabled'):
                    debug_info = f"\n\n[Debug] Filtering: {filtering_info.get('original_count', 0)} → {filtering_info.get('filtered_count', 0)} results"
                    if filtering_info.get('best_distance') is not None:
                        debug_info += f", Best match: {filtering_info['best_distance']:.4f}"
                    debug_info += f", Hard threshold: {filtering_info.get('hard_threshold_value', 'N/A')}"
                    response += debug_info
            
            return response
            
        except Exception as e:
            return f"An unexpected error occurred during RAG processing: {e}"
    
    def process_query_legacy(self, query_prompt: str) -> str:
        """
        Legacy method: Process a complete RAG query using embedding-based retrieval.
        Kept for backward compatibility and comparison.
        
        Args:
            query_prompt (str): The user's query
            
        Returns:
            str: The final response or error message
        """
        try:
            if not query_prompt.strip():
                return "Please enter a non-empty query."
            
            if config.VERBOSE_LOGGING:
                print(f"\n--- Processing Query (Legacy): '{query_prompt}' ---")
            
            # Step 1: Generate embedding for the query
            embedding_result = self.generate_embedding(query_prompt)
            if "error" in embedding_result:
                return f"Error: {embedding_result['error']}\n{embedding_result.get('suggestion', '')}"
            
            # Step 2: Retrieve relevant documents using embeddings
            retrieval_result = self.retrieve_relevant_documents_legacy(
                embedding_result["embeddings"]
            )
            if "error" in retrieval_result:
                return f"Error: {retrieval_result['error']}"
            
            # Step 3: Generate response with context
            generation_result = self.generate_response(
                query_prompt, 
                retrieval_result["retrieved_data"]
            )
            if "error" in generation_result:
                return f"Error: {generation_result['error']}\n{generation_result.get('suggestion', '')}"
            
            return generation_result["response"]
            
        except Exception as e:
            return f"An unexpected error occurred during RAG processing: {e}"
    
    def get_models_info(self) -> dict:
        """
        Get information about the models being used.
        
        Returns:
            dict: Model information
        """
        return {
            "embedding_model": self.embedding_model,
            "generation_model": self.generation_model,
            "sentence_transformer_model": config.SENTENCE_TRANSFORMER_MODEL
        }
