"""
Enhanced RAG Processor Module

This module extends the RAG processor with enhanced response formatting
and better prompt engineering for more colorful and structured responses.
"""

import ollama
from config import config
from chromadb_manager import ChromaDBManager
from rag_processor import RAGProcessor


class EnhancedRAGProcessor(RAGProcessor):
    """Enhanced RAG processor with better response formatting."""
    
    def __init__(self, chromadb_manager: ChromaDBManager, 
                 embedding_model: str = None, generation_model: str = None):
        """Initialize enhanced RAG processor."""
        super().__init__(chromadb_manager, embedding_model, generation_model)
    
    def generate_enhanced_response(self, prompt: str, context_data: str = "") -> dict:
        """
        Generate an enhanced response with better formatting and structure.
        
        Args:
            prompt (str): User prompt/query
            context_data (str): Retrieved context data to include
            
        Returns:
            dict: Generated response or error dict
        """
        try:
            if config.VERBOSE_LOGGING:
                print(f"Generating enhanced response using '{self.generation_model}'...")
            
            # Construct enhanced prompt with formatting instructions
            if context_data and context_data != "No relevant information found.":
                full_prompt = self._create_enhanced_prompt_with_context(prompt, context_data)
            else:
                full_prompt = self._create_enhanced_prompt_without_context(prompt)
            
            output = ollama.generate(
                model=self.generation_model,
                prompt=full_prompt
            )
            
            response_text = output.get('response', 'No response generated.')
            return {
                "response": response_text,
                "full_prompt": full_prompt if config.DEBUG_MODE else None,
                "enhanced": True
            }
            
        except ollama.ResponseError as e:
            return {
                "error": f"Ollama generation error: {e}",
                "suggestion": f"Please ensure Ollama server is running and model '{self.generation_model}' is pulled."
            }
        except Exception as e:
            return {"error": f"Unexpected error generating response: {e}"}
    
    def _create_enhanced_prompt_with_context(self, prompt: str, context_data: str) -> str:
        """Create an enhanced prompt with context and formatting instructions."""
        return f"""You are a helpful AI assistant. Please provide a well-structured, informative response based on the given context.

**Context Information:**
{context_data}

**User Question:**
{prompt}

**Formatting Instructions:**
- Use **bold text** for important terms, key concepts, and emphasis
- Use *italic text* for definitions, explanations, and subtle emphasis
- Use ***bold italic*** for critical information that needs maximum attention
- Use `inline code` for technical terms, commands, or code snippets
- Use bullet points (•) or numbered lists for structured information
- Use headings (# ## ###) to organize longer responses
- Use ==highlighted text== for warnings or special notes
- Use > quotes for important citations or references

**Content Instructions:**
- Provide a clear, comprehensive answer based on the context
- **Highlight important information** using appropriate formatting
- If the context doesn't fully answer the question, mention what information might be missing
- Be concise but thorough
- Use examples when helpful
- Make key points stand out with proper emphasis

**Response:**"""
    
    def _create_enhanced_prompt_without_context(self, prompt: str) -> str:
        """Create an enhanced prompt without context but with formatting instructions."""
        return f"""You are a helpful AI assistant. Please provide a well-structured, informative response to the user's question.

**User Question:**
{prompt}

**Formatting Instructions:**
- Use **bold text** for important terms, key concepts, and emphasis
- Use *italic text* for definitions, explanations, and subtle emphasis
- Use ***bold italic*** for critical information that needs maximum attention
- Use `inline code` for technical terms, commands, or code snippets
- Use bullet points (•) or numbered lists for structured information
- Use headings (# ## ###) to organize longer responses
- Use ==highlighted text== for warnings or special notes
- Use > quotes for important citations or references

**Content Instructions:**
- Provide a clear, comprehensive answer
- **Highlight important information** using appropriate formatting
- Be concise but thorough
- Use examples when helpful
- If you're not certain about something, mention it clearly
- Make key points stand out with proper emphasis

**Response:**"""
    
    def process_enhanced_query(self, query_prompt: str) -> str:
        """
        Process a complete RAG query with enhanced formatting and dynamic distance filtering.
        
        Args:
            query_prompt (str): The user's query
            
        Returns:
            str: The final enhanced response or error message
        """
        try:
            if not query_prompt.strip():
                return "Please enter a non-empty query."
            
            if config.VERBOSE_LOGGING:
                print(f"\n--- Processing Enhanced Query: '{query_prompt}' ---")
            
            # Use direct text-based retrieval with dynamic filtering (new approach)
            retrieval_result = self.retrieve_relevant_documents(query_prompt)
            if "error" in retrieval_result:
                return f"**Error:** {retrieval_result['error']}"
            
            # Generate enhanced response with context
            generation_result = self.generate_enhanced_response(
                query_prompt, 
                retrieval_result["retrieved_data"]
            )
            if "error" in generation_result:
                return f"**Error:** {generation_result['error']}\n\n{generation_result.get('suggestion', '')}"
            
            # Add filtering information to response if in debug mode
            response = generation_result["response"]
            if config.DISTANCE_DEBUG_MODE and retrieval_result.get('filtering_info'):
                filtering_info = retrieval_result['filtering_info']
                if filtering_info.get('filtering_enabled'):
                    debug_info = f"\n\n**[Debug]** Filtering: {filtering_info.get('original_count', 0)} → {filtering_info.get('filtered_count', 0)} results"
                    if filtering_info.get('best_distance') is not None:
                        debug_info += f", Best match: {filtering_info['best_distance']:.4f}"
                    response += debug_info
            
            return response
            
        except Exception as e:
            return f"**An unexpected error occurred during RAG processing:** {e}"
    
    def get_response_with_metadata(self, query_prompt: str) -> dict:
        """
        Get response with additional metadata for enhanced display.
        
        Args:
            query_prompt (str): The user's query
            
        Returns:
            dict: Response with metadata
        """
        try:
            # Process the query
            response = self.process_enhanced_query(query_prompt)
            
            # Get collection info for metadata
            collection_info = self.chromadb_manager.get_collection_info()
            
            return {
                "response": response,
                "query": query_prompt,
                "metadata": {
                    "documents_in_collection": collection_info.get("count", 0),
                    "embedding_model": self.embedding_model,
                    "generation_model": self.generation_model,
                    "timestamp": self._get_timestamp()
                }
            }
            
        except Exception as e:
            return {
                "response": f"Error processing query: {e}",
                "query": query_prompt,
                "metadata": {"error": True}
            }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for metadata."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
