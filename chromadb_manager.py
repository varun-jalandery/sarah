"""
ChromaDB Manager Module

This module handles all ChromaDB operations including:
- Adding context to collections
- Clearing collections
- Collection initialization and management
"""

# Import telemetry disabler FIRST
import disable_telemetry

import os
import chromadb
from chromadb.config import Settings
from datetime import datetime
from chromadb.utils import embedding_functions
from config import config
from colors import print_success, print_error, print_warning, print_info


class ChromaDBManager:
    """Manages ChromaDB operations and collection management."""
    
    def __init__(self, db_path: str = None, collection_name: str = None):
        """
        Initialize ChromaDB manager.
        
        Args:
            db_path (str): Path to ChromaDB storage. Uses config default if None.
            collection_name (str): Name of the collection. Uses config default if None.
        """
        self.db_path = db_path or config.CHROMA_DB_PATH
        self.collection_name = collection_name or config.COLLECTION_NAME
        self.client = None
        self.collection = None
        
    def initialize_client(self) -> bool:
        """
        Initialize ChromaDB client and collection.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Set environment variable to disable telemetry completely
            import os
            os.environ['ANONYMIZED_TELEMETRY'] = 'False'
            
            # Disable telemetry to avoid the capture() error
            settings = Settings(
                anonymized_telemetry=False,
                allow_reset=True,
                is_persistent=True
            )
            
            self.client = chromadb.PersistentClient(path=self.db_path, settings=settings)
            
            # Use sentence transformer embedding function for consistency
            sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=config.SENTENCE_TRANSFORMER_MODEL
            )
            
            # Get or create collection with the same embedding function
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=sentence_transformer_ef
            )
            
            if config.VERBOSE_LOGGING:
                print(f"Successfully connected to ChromaDB collection: '{self.collection_name}'")
                print(f"Using embedding function: {config.SENTENCE_TRANSFORMER_MODEL}")
            
            return True
            
        except Exception as e:
            print(f"Error: Could not initialize ChromaDB or retrieve collection '{self.collection_name}'.")
            print(f"Please ensure '{self.db_path}' exists and contains the collection.")
            print(f"Error details: {e}")
            return False
    
    def add_context(self, text_content: str, source_label: str = "user_input") -> bool:
        """
        Adds multi-line text content to ChromaDB collection.
        
        Args:
            text_content (str): The text content to add to ChromaDB
            source_label (str): Label to identify the source of this content
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not text_content.strip():
                print("Error: Cannot add empty content to ChromaDB.")
                return False
            
            if not self.collection:
                print("Error: ChromaDB collection not initialized.")
                return False
            
            # Generate a unique ID with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            doc_id = f"{source_label}_{timestamp}"
            
            # Prepare metadata
            metadata = {
                "source": source_label,
                "timestamp": timestamp,
                "content_type": "user_context",
                "added_via": "chromadb_manager"
            }
            
            # Add the document to ChromaDB
            self.collection.add(
                documents=[text_content.strip()],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            if config.VERBOSE_LOGGING:
                print(f"Successfully added context to ChromaDB with ID: {doc_id}")
            
            return True
            
        except Exception as e:
            print(f"Error adding context to ChromaDB: {e}")
            return False
    
    def clear_collection(self) -> bool:
        """
        Clears all documents from the ChromaDB collection.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.collection:
                print("Error: ChromaDB collection not initialized.")
                return False
            
            # Get current document count
            current_count = self.collection.count()
            
            if current_count == 0:
                print("ChromaDB collection is already empty.")
                return True
            
            # Get all document IDs and delete them
            all_docs = self.collection.get()
            if all_docs and all_docs.get('ids'):
                self.collection.delete(ids=all_docs['ids'])
                print(f"✓ Successfully cleared {current_count} document(s) from ChromaDB collection!")
                
                if config.VERBOSE_LOGGING:
                    print(f"Collection '{self.collection.name}' is now empty.")
                return True
            else:
                print("No documents found to delete.")
                return True
                
        except Exception as e:
            print(f"✗ Error clearing ChromaDB collection: {e}")
            if config.DEBUG_MODE:
                import traceback
                traceback.print_exc()
            return False
    
    def get_collection_info(self) -> dict:
        """
        Get information about the current collection.
        
        Returns:
            dict: Collection information including count, name, etc.
        """
        if not self.collection:
            return {"error": "Collection not initialized"}
        
        try:
            count = self.collection.count()
            return {
                "name": self.collection_name,
                "count": count,
                "db_path": self.db_path
            }
        except Exception as e:
            return {"error": f"Failed to get collection info: {e}"}
    
    def query_collection(self, query_embeddings: list, n_results: int = None) -> dict:
        """
        Query the collection with embeddings.
        
        Args:
            query_embeddings (list): List of embeddings to query with
            n_results (int): Number of results to return. Uses config default if None.
        
        Returns:
            dict: Query results from ChromaDB
        """
        if not self.collection:
            return {"error": "Collection not initialized"}
        
        try:
            n_results = n_results or config.MAX_RESULTS
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results
            )
            return results
        except Exception as e:
            return {"error": f"Failed to query collection: {e}"}
    
    def query_with_text(self, query_text: str, n_results: int = None) -> dict:
        """
        Query the collection with text (uses ChromaDB's built-in embedding).
        
        Args:
            query_text (str): Text to query with
            n_results (int): Number of results to return
        
        Returns:
            dict: Query results from ChromaDB
        """
        if not self.collection:
            return {"error": "Collection not initialized"}
        
        try:
            n_results = n_results or config.MAX_RESULTS
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results
        except Exception as e:
            return {"error": f"Failed to query collection with text: {e}"}
    
    def query_with_dynamic_distance_filter(self, query_text: str, n_results: int = None) -> dict:
        """
        Query with dynamic distance-based filtering for improved accuracy.
        
        This method implements several filtering strategies:
        1. Base threshold filtering - removes results beyond a base threshold
        2. Dynamic ratio filtering - filters based on the best result's distance
        3. Adaptive filtering - adjusts thresholds based on result quality
        
        Args:
            query_text (str): Text to query with
            n_results (int): Desired number of results
        
        Returns:
            dict: Filtered query results with distance information
        """
        if not self.collection:
            return {"error": "Collection not initialized"}
        
        if not config.ENABLE_DISTANCE_FILTERING:
            # Fall back to regular query if filtering is disabled
            return self.query_with_text(query_text, n_results)
        
        try:
            n_results = n_results or config.MAX_RESULTS
            
            # Query with extra results to allow for filtering
            query_size = max(n_results * 3, config.MIN_RESULTS_FOR_FILTERING * 2)
            raw_results = self.collection.query(
                query_texts=[query_text],
                n_results=query_size
            )
            
            if not raw_results.get('distances') or not raw_results['distances'][0]:
                if config.DISTANCE_DEBUG_MODE:
                    print_warning("No distance information available in query results")
                return raw_results
            
            distances = raw_results['distances'][0]
            documents = raw_results['documents'][0] if raw_results.get('documents') else []
            metadatas = raw_results['metadatas'][0] if raw_results.get('metadatas') else []
            ids = raw_results['ids'][0] if raw_results.get('ids') else []
            
            if not distances or len(distances) == 0:
                if config.DISTANCE_DEBUG_MODE:
                    print_warning("Empty distance list in query results")
                return raw_results
            
            # Apply hard distance threshold first (absolute cutoff)
            hard_filtered_indices = [i for i, dist in enumerate(distances) 
                                   if dist <= config.HARD_DISTANCE_THRESHOLD]
            
            if not hard_filtered_indices:
                # No results pass the hard threshold - return empty results
                if config.DISTANCE_DEBUG_MODE:
                    print_warning(f"No results passed hard distance threshold of {config.HARD_DISTANCE_THRESHOLD}")
                    print_warning(f"Best available distance was: {min(distances):.4f}")
                
                return {
                    'documents': [[]],
                    'metadatas': [[]],
                    'distances': [[]],
                    'ids': [[]],
                    'filtering_info': {
                        'original_count': len(distances),
                        'filtered_count': 0,
                        'filtering_enabled': True,
                        'hard_threshold_applied': True,
                        'hard_threshold_value': config.HARD_DISTANCE_THRESHOLD,
                        'best_distance': min(distances) if distances else None,
                        'rejected_by_hard_threshold': True
                    }
                }
            
            # Filter the original data to only include results that passed hard threshold
            hard_filtered_distances = [distances[i] for i in hard_filtered_indices]
            hard_filtered_documents = [documents[i] for i in hard_filtered_indices] if documents else []
            hard_filtered_metadatas = [metadatas[i] for i in hard_filtered_indices] if metadatas else []
            hard_filtered_ids = [ids[i] for i in hard_filtered_indices] if ids else []
            
            # Apply dynamic distance filtering to the hard-filtered results
            relative_filtered_indices = self._apply_dynamic_distance_filtering(hard_filtered_distances, query_text)
            
            # Convert relative indices back to original indices
            filtered_indices = [hard_filtered_indices[i] for i in relative_filtered_indices]
            
            # Limit to requested number of results
            filtered_indices = filtered_indices[:n_results]
            
            # Build filtered results
            filtered_results = {
                'documents': [[documents[i] for i in filtered_indices]] if documents else [[]],
                'metadatas': [[metadatas[i] for i in filtered_indices]] if metadatas else [[]],
                'distances': [[distances[i] for i in filtered_indices]],
                'ids': [[ids[i] for i in filtered_indices]] if ids else [[]],
                'filtering_info': {
                    'original_count': len(distances),
                    'filtered_count': len(filtered_indices),
                    'filtering_enabled': True,
                    'hard_threshold_applied': True,
                    'hard_threshold_value': config.HARD_DISTANCE_THRESHOLD,
                    'hard_threshold_passed': len(hard_filtered_indices),
                    'best_distance': min(distances) if distances else None,
                    'worst_accepted_distance': max([distances[i] for i in filtered_indices]) if filtered_indices else None
                }
            }
            
            if config.DISTANCE_DEBUG_MODE:
                self._print_distance_debug_info(distances, filtered_indices, query_text)
            
            return filtered_results
            
        except Exception as e:
            print_error(f"Error in dynamic distance filtering: {e}")
            if config.DEBUG_MODE:
                import traceback
                traceback.print_exc()
            # Fall back to regular query on error
            return self.query_with_text(query_text, n_results)
    
    def _apply_dynamic_distance_filtering(self, distances: list, query_text: str = "") -> list:
        """
        Apply dynamic distance filtering logic to determine which results to keep.
        
        Args:
            distances (list): List of distances from ChromaDB query
            query_text (str): Original query text for context
        
        Returns:
            list: Indices of results to keep, sorted by distance (best first)
        """
        if not distances:
            return []
        
        # Sort indices by distance (best/lowest first)
        sorted_indices = sorted(range(len(distances)), key=lambda i: distances[i])
        
        if len(distances) < config.MIN_RESULTS_FOR_FILTERING:
            # Not enough results for meaningful filtering
            return sorted_indices
        
        best_distance = distances[sorted_indices[0]]
        
        # Strategy 1: Base threshold filtering
        base_filtered = [i for i in sorted_indices 
                        if distances[i] <= config.BASE_DISTANCE_THRESHOLD]
        
        # Strategy 2: Dynamic ratio filtering (relative to best result)
        dynamic_threshold = best_distance / config.DYNAMIC_THRESHOLD_RATIO
        ratio_filtered = [i for i in sorted_indices 
                         if distances[i] <= dynamic_threshold]
        
        # Strategy 3: Adaptive filtering based on result quality
        adaptive_filtered = self._apply_adaptive_filtering(distances, sorted_indices, best_distance)
        
        # Combine strategies: use the most restrictive that still gives reasonable results
        candidates = [base_filtered, ratio_filtered, adaptive_filtered]
        
        # Choose the filtering strategy that provides the best balance
        chosen_filtered = self._choose_best_filtering_strategy(candidates, distances, sorted_indices)
        
        return chosen_filtered if chosen_filtered else sorted_indices[:1]  # Always return at least the best result
    
    def _apply_adaptive_filtering(self, distances: list, sorted_indices: list, best_distance: float) -> list:
        """
        Apply adaptive filtering based on the distribution of distances.
        
        Args:
            distances (list): List of distances
            sorted_indices (list): Indices sorted by distance
            best_distance (float): The best (lowest) distance
        
        Returns:
            list: Filtered indices
        """
        if len(sorted_indices) < 3:
            return sorted_indices
        
        # Calculate distance gaps between consecutive results
        gaps = []
        for i in range(len(sorted_indices) - 1):
            current_dist = distances[sorted_indices[i]]
            next_dist = distances[sorted_indices[i + 1]]
            gaps.append(next_dist - current_dist)
        
        if not gaps:
            return sorted_indices
        
        # Find the largest gap (indicates a quality drop)
        max_gap_index = gaps.index(max(gaps))
        
        # If the largest gap is significant, cut off after it
        avg_gap = sum(gaps) / len(gaps)
        if gaps[max_gap_index] > avg_gap * 2:  # Gap is more than 2x average
            return sorted_indices[:max_gap_index + 1]
        
        return sorted_indices
    
    def _choose_best_filtering_strategy(self, candidates: list, distances: list, sorted_indices: list) -> list:
        """
        Choose the best filtering strategy from candidates.
        
        Args:
            candidates (list): List of filtered index lists from different strategies
            distances (list): Original distances
            sorted_indices (list): All indices sorted by distance
        
        Returns:
            list: Best filtered indices
        """
        # Remove empty candidates
        valid_candidates = [c for c in candidates if c]
        
        if not valid_candidates:
            return sorted_indices[:config.MIN_RESULTS_FOR_FILTERING]
        
        # Prefer the strategy that keeps at least MIN_RESULTS_FOR_FILTERING results
        # but isn't too permissive
        for candidate in sorted(valid_candidates, key=len):
            if len(candidate) >= config.MIN_RESULTS_FOR_FILTERING:
                return candidate
        
        # If no strategy meets the minimum, use the one with the most results
        return max(valid_candidates, key=len)
    
    def _print_distance_debug_info(self, distances: list, filtered_indices: list, query_text: str):
        """Print debug information about distance filtering."""
        print_info(f"\n--- Distance Filtering Debug Info ---")
        print_info(f"Query: '{query_text[:50]}{'...' if len(query_text) > 50 else ''}'")
        print_info(f"Original results: {len(distances)}")
        print_info(f"Filtered results: {len(filtered_indices)}")
        
        if distances:
            print_info(f"Distance range: {min(distances):.4f} - {max(distances):.4f}")
            print_info(f"Hard threshold: {config.HARD_DISTANCE_THRESHOLD}")
            print_info(f"Base threshold: {config.BASE_DISTANCE_THRESHOLD}")
            print_info(f"Dynamic ratio: {config.DYNAMIC_THRESHOLD_RATIO}")
        
        print_info("Filtered results:")
        for i, idx in enumerate(filtered_indices[:5]):  # Show top 5
            print_info(f"  {i+1}. Distance: {distances[idx]:.4f}")
        
        if len(filtered_indices) > 5:
            print_info(f"  ... and {len(filtered_indices) - 5} more")
        print_info("--- End Debug Info ---\n")
