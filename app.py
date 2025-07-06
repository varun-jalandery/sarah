"""
Main Application Module

This module contains the main application logic and interactive loop.
It orchestrates all other modules to provide the complete RAG experience.
"""

# Import telemetry disabler FIRST to prevent ChromaDB telemetry errors
import disable_telemetry

import sys
from config import config
from chromadb_manager import ChromaDBManager
from rag_processor import RAGProcessor
from enhanced_rag_processor import EnhancedRAGProcessor
from interactive_commands import InteractiveCommands
from colors import (
    Colors, print_success, print_error, print_warning, print_info, 
    print_header, print_subheader, colorize
)
from colorful_response_formatter import print_colorful_response
from enhanced_formatting import print_enhanced_response


class RAGApplication:
    """Main RAG application class that orchestrates all components."""
    
    def __init__(self):
        """Initialize the Sarah with all components."""
        self.chromadb_manager = None
        self.rag_processor = None
        self.commands = None
        self.initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize all application components.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Print configuration if debug mode is enabled
            if config.DEBUG_MODE:
                config.print_config()
            
            print_info("Initializing ChromaDB client...")
            
            # Initialize ChromaDB manager
            self.chromadb_manager = ChromaDBManager()
            if not self.chromadb_manager.initialize_client():
                return False
            
            # Initialize RAG processor (use enhanced version for better formatting)
            self.rag_processor = EnhancedRAGProcessor(self.chromadb_manager)
            
            # Initialize interactive commands
            self.commands = InteractiveCommands(self.chromadb_manager, self.rag_processor)
            
            self.initialized = True
            print_success("Sarah initialized successfully!")
            return True
            
        except Exception as e:
            print_error(f"Error during Sarah initialization: {e}")
            return False
    
    def run_interactive_mode(self):
        """Run the main interactive loop."""
        if not self.initialized:
            print_error("Sarah not initialized. Call initialize() first.")
            return
        
        # Print startup help
        self.commands.print_startup_help()
        
        # Main interactive loop
        while True:
            try:
                # Create colorized prompt
                prompt_text = colorize("\n💬 Your query: ", Colors.BRIGHT_WHITE, Colors.BOLD)
                user_input = input(prompt_text).strip()
                
                # Handle empty input
                if not user_input:
                    print_warning("Please enter a query or use a command (type '/help' for options).")
                    continue
                
                # Check if input is a command
                if self.commands.is_command(user_input):
                    result = self.commands.execute_command(user_input)
                    
                    # Print message if provided
                    if result.get('message'):
                        print(result['message'])
                    
                    # Handle exit action
                    if result.get('action') == 'exit':
                        break
                    
                    continue
                
                # Process regular query using enhanced RAG
                print_info("Processing your query...")
                response = self.rag_processor.process_enhanced_query(user_input)
                
                # Print beautifully formatted colorful response with enhanced emphasis
                print_enhanced_response(response, user_input)
                
            except KeyboardInterrupt:
                print(colorize("\n\n👋 Exiting interactive mode. Goodbye!", Colors.BRIGHT_CYAN))
                break
            except Exception as e:
                print_error(f"Error during interactive session: {e}")
                if config.DEBUG_MODE:
                    import traceback
                    traceback.print_exc()
        
        print_info("Script finished.")
    
    def process_single_query(self, query: str) -> str:
        """
        Process a single query without interactive mode.
        
        Args:
            query (str): Query to process
            
        Returns:
            str: Response from the RAG system
        """
        if not self.initialized:
            return "Error: Sarah not initialized."
        
        return self.rag_processor.process_enhanced_query(query)
    
    def add_context(self, text: str, source_label: str = "api_input") -> bool:
        """
        Add context to the system programmatically.
        
        Args:
            text (str): Text content to add
            source_label (str): Label for the source
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.initialized:
            return False
        
        return self.chromadb_manager.add_context(text, source_label)
    
    def clear_context(self) -> bool:
        """
        Clear all context from the system.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.initialized:
            return False
        
        return self.chromadb_manager.clear_collection()
    
    def get_system_info(self) -> dict:
        """
        Get system information.
        
        Returns:
            dict: System information including models, collection info, etc.
        """
        if not self.initialized:
            return {"error": "Sarah not initialized"}
        
        collection_info = self.chromadb_manager.get_collection_info()
        models_info = self.rag_processor.get_models_info()
        
        return {
            "collection": collection_info,
            "models": models_info,
            "config": {
                "debug_mode": config.DEBUG_MODE,
                "verbose_logging": config.VERBOSE_LOGGING,
                "max_results": config.MAX_RESULTS,
                "max_retrieved_data_length": config.MAX_RETRIEVED_DATA_LENGTH
            }
        }


def main():
    """Main entry point for the application."""
    print_header("🚀 Starting Sarah")
    
    app = RAGApplication()
    
    if not app.initialize():
        print_error("Failed to initialize Sarah. Exiting.")
        sys.exit(1)
    
    # Run interactive mode
    app.run_interactive_mode()


if __name__ == "__main__":
    main()
