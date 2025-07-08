"""
Interactive Commands Module

This module handles all interactive commands for the RAG system:
- /context command for adding multi-line context
- /clear command for clearing the database
- /help command for showing help
- Command parsing and validation
"""

from chromadb_manager import ChromaDBManager
from config import config
from colors import (
    Colors, print_success, print_error, print_warning, print_info, 
    print_header, print_subheader, print_command, print_dim, colorize
)


class InteractiveCommands:
    """Handles interactive commands for the RAG system."""
    
    def __init__(self, chromadb_manager: ChromaDBManager, rag_processor=None):
        """
        Initialize interactive commands handler.
        
        Args:
            chromadb_manager (ChromaDBManager): ChromaDB manager instance
            rag_processor: RAG processor instance for model switching
        """
        self.chromadb_manager = chromadb_manager
        self.rag_processor = rag_processor
        self.commands = {
            '/bye': self._handle_bye,
            '/context': self._handle_context,
            '/clear': self._handle_clear,
            '/help': self._handle_help,
            '/info': self._handle_info,
            '/model': self._handle_model
        }
    
    def is_command(self, user_input: str) -> bool:
        """
        Check if user input is a command.
        
        Args:
            user_input (str): User input to check
            
        Returns:
            bool: True if input is a command, False otherwise
        """
        return user_input.strip().startswith('/')
    
    def execute_command(self, command: str) -> dict:
        """
        Execute a command and return the result.
        
        Args:
            command (str): Command to execute
            
        Returns:
            dict: Command execution result with 'action' and optional 'message'
        """
        command = command.strip().lower()
        
        if command in self.commands:
            return self.commands[command]()
        else:
            return {
                'action': 'continue',
                'message': f"Unknown command: {command}\nType '/help' to see available commands."
            }
    
    def _handle_bye(self) -> dict:
        """Handle the /bye command."""
        return {
            'action': 'exit',
            'message': colorize("👋 Exiting interactive mode. Goodbye!", Colors.BRIGHT_CYAN)
        }
    
    def _handle_context(self) -> dict:
        """Handle the /context command for adding multi-line context."""
        print_header("\n📝 Context Input Mode")
        print_info("Enter your multi-line context below.")
        print_dim("Type 'END' on a new line when finished, or 'CANCEL' to abort.")
        print(colorize("=" * 50, Colors.CYAN))
        
        lines = []
        while True:
            try:
                line = input()
                if line.strip().upper() == 'END':
                    break
                elif line.strip().upper() == 'CANCEL':
                    return {
                        'action': 'continue',
                        'message': colorize("❌ Context input cancelled.", Colors.YELLOW)
                    }
                else:
                    lines.append(line)
            except KeyboardInterrupt:
                return {
                    'action': 'continue',
                    'message': colorize("\n❌ Context input cancelled.", Colors.YELLOW)
                }
        
        if not lines:
            return {
                'action': 'continue',
                'message': colorize("⚠️  No content entered. Context not saved.", Colors.YELLOW)
            }
        
        # Join all lines into a single text block
        context_text = '\n'.join(lines)
        
        # Show preview of what will be saved
        preview_length = 200
        preview = context_text[:preview_length]
        if len(context_text) > preview_length:
            preview += "..."
        
        print_subheader(f"\n📋 Preview of context to be saved:")
        print(colorize("-" * 30, Colors.CYAN))
        print(preview)
        print(colorize("-" * 30, Colors.CYAN))
        print_info(f"Total length: {colorize(str(len(context_text)), Colors.BRIGHT_WHITE)} characters")
        
        # Confirm before saving
        confirm_prompt = colorize("\n💾 Save this context to ChromaDB? (y/N): ", Colors.BRIGHT_WHITE)
        confirm = input(confirm_prompt).strip().lower()
        if confirm in ['y', 'yes']:
            if self.chromadb_manager.add_context(context_text):
                return {
                    'action': 'continue',
                    'message': colorize("✅ Context successfully saved to ChromaDB!", Colors.BRIGHT_GREEN)
                }
            else:
                return {
                    'action': 'continue',
                    'message': colorize("❌ Failed to save context to ChromaDB.", Colors.BRIGHT_RED)
                }
        else:
            return {
                'action': 'continue',
                'message': colorize("📝 Context not saved.", Colors.YELLOW)
            }
    
    def _handle_clear(self) -> dict:
        """Handle the /clear command for clearing all documents."""
        try:
            # Get current document count
            collection_info = self.chromadb_manager.get_collection_info()
            if "error" in collection_info:
                return {
                    'action': 'continue',
                    'message': colorize(f"❌ Error getting collection info: {collection_info['error']}", Colors.BRIGHT_RED)
                }
            
            current_count = collection_info.get('count', 0)
            
            if current_count == 0:
                return {
                    'action': 'continue',
                    'message': colorize("📭 ChromaDB collection is already empty.", Colors.BRIGHT_BLUE)
                }
            
            print_header(f"\n🗑️  Clear ChromaDB Collection")
            print_info(f"Current collection contains {colorize(str(current_count), Colors.BRIGHT_WHITE)} document(s).")
            print_warning("This will permanently delete ALL documents from the collection!")
            
            # Double confirmation for safety
            confirm1_prompt = colorize(f"\n🤔 Are you sure you want to clear all context? (y/N): ", Colors.BRIGHT_WHITE)
            confirm1 = input(confirm1_prompt).strip().lower()
            if confirm1 not in ['y', 'yes']:
                return {
                    'action': 'continue',
                    'message': colorize("❌ Clear operation cancelled.", Colors.YELLOW)
                }
            
            confirm2_prompt = colorize("⚠️  This action cannot be undone. Type 'DELETE' to confirm: ", Colors.BRIGHT_RED)
            confirm2 = input(confirm2_prompt).strip()
            if confirm2 != 'DELETE':
                return {
                    'action': 'continue',
                    'message': colorize("❌ Clear operation cancelled.", Colors.YELLOW)
                }
            
            # Perform the clear operation
            if self.chromadb_manager.clear_collection():
                return {
                    'action': 'continue',
                    'message': colorize(f"✅ Successfully cleared {current_count} document(s) from ChromaDB collection!", Colors.BRIGHT_GREEN)
                }
            else:
                return {
                    'action': 'continue',
                    'message': colorize("❌ Failed to clear ChromaDB collection.", Colors.BRIGHT_RED)
                }
                
        except Exception as e:
            return {
                'action': 'continue',
                'message': colorize(f"❌ Error during clear operation: {e}", Colors.BRIGHT_RED)
            }
    
    def _handle_help(self) -> dict:
        """Handle the /help command."""
        help_lines = [
            colorize("\n📚 Available commands:", Colors.BRIGHT_CYAN, Colors.BOLD),
            colorize("  /bye     ", Colors.BRIGHT_MAGENTA) + colorize("- Exit the program", Colors.WHITE),
            colorize("  /context ", Colors.BRIGHT_MAGENTA) + colorize("- Add multi-line context to ChromaDB", Colors.WHITE),
            colorize("  /clear   ", Colors.BRIGHT_MAGENTA) + colorize("- Clear all documents from ChromaDB", Colors.WHITE),
            colorize("  /model   ", Colors.BRIGHT_MAGENTA) + colorize("- Switch LLM model (gemma3:4b/mistral:7b)", Colors.WHITE),
            colorize("  /info    ", Colors.BRIGHT_MAGENTA) + colorize("- Show system information", Colors.WHITE),
            colorize("  /help    ", Colors.BRIGHT_MAGENTA) + colorize("- Show this help message", Colors.WHITE),
            "",
            colorize("💬 Or enter any query to get an AI response based on your stored context.", Colors.BRIGHT_BLUE)
        ]
        
        return {
            'action': 'continue',
            'message': '\n'.join(help_lines)
        }
    
    def _handle_model(self) -> dict:
        """Handle the /model command for switching LLM models."""
        if not self.rag_processor:
            return {
                'action': 'continue',
                'message': colorize("❌ Model switching not available - RAG processor not initialized.", Colors.BRIGHT_RED)
            }
        
        print_header("\n🤖 LLM Model Switcher")
        print_info("Available models:")
        print(colorize("  1. ", Colors.BRIGHT_BLUE) + colorize("gemma3:4b", Colors.BRIGHT_WHITE) + colorize(" - Gemma model 4 billion params", Colors.WHITE))
        print(colorize("  2. ", Colors.BRIGHT_BLUE) + colorize("mistral:7b", Colors.BRIGHT_WHITE) + colorize(" - Mistral is a 7B parameter model, distributed with the Apache license", Colors.WHITE))
        print(colorize("  3. ", Colors.BRIGHT_BLUE) + colorize("gemma3:27b", Colors.BRIGHT_WHITE) + colorize(" -Gemma model 27 billion params", Colors.WHITE))
        print(colorize("  4. ", Colors.BRIGHT_BLUE) + colorize("gemma3n:e4b", Colors.BRIGHT_WHITE) + colorize(" -Gemma model for everday use on everyday devices like phones, laptops :-)", Colors.WHITE))
        
        current_model = getattr(self.rag_processor, 'generation_model', 'Unknown')
        print_info(f"Current model: {colorize(current_model, Colors.BRIGHT_CYAN)}")
        
        try:
            choice_prompt = colorize("\n🔧 Enter model choice (1-2) or model name, or 'cancel' to abort: ", Colors.BRIGHT_WHITE)
            choice = input(choice_prompt).strip().lower()
            
            if choice in ['cancel', 'c']:
                return {
                    'action': 'continue',
                    'message': colorize("❌ Model switching cancelled.", Colors.YELLOW)
                }
            
            # Map choices to model names
            model_map = {
                '1': 'gemma3:4b',
                '2': 'mistral:7b',
                '3': 'gemma3:27b',
                '4': 'gemma3n:e4b',
                'gemma3:27b': 'gemma3:27b',
                'gemma3:4b': 'gemma3:4b',
                'mistral:7b': 'mistral:7b'
                'gemma3n:e4b': 'gemma3n:e4b'
            }
            
            if choice not in model_map:
                return {
                    'action': 'continue',
                    'message': colorize(f"❌ Invalid choice: {choice}. Please choose 1-2 or a valid model name.", Colors.BRIGHT_RED)
                }
            
            new_model = model_map[choice]
            
            # Check if it's the same model
            if new_model == current_model:
                return {
                    'action': 'continue',
                    'message': colorize(f"ℹ️  Already using model: {new_model}", Colors.BRIGHT_BLUE)
                }
            
            # Confirm the switch
            confirm_prompt = colorize(f"\n🔄 Switch from '{current_model}' to '{new_model}'? (y/N): ", Colors.BRIGHT_WHITE)
            confirm = input(confirm_prompt).strip().lower()
            
            if confirm not in ['y', 'yes']:
                return {
                    'action': 'continue',
                    'message': colorize("❌ Model switch cancelled.", Colors.YELLOW)
                }
            
            # Perform the model switch
            old_model = current_model
            self.rag_processor.generation_model = new_model
            
            # Test the new model by checking if it's available
            try:
                import ollama
                # Try to get model info to verify it exists
                models = ollama.list()
                available_models = [model['name'] for model in models.get('models', [])]
                
                if not any(new_model in model_name for model_name in available_models):
                    print_warning(f"⚠️  Model '{new_model}' may not be pulled yet.")
                    print_info(f"You may need to run: ollama pull {new_model}")
                
            except Exception as e:
                print_warning(f"⚠️  Could not verify model availability: {e}")
            
            return {
                'action': 'continue',
                'message': colorize(f"✅ Successfully switched from '{old_model}' to '{new_model}'!", Colors.BRIGHT_GREEN)
            }
            
        except KeyboardInterrupt:
            return {
                'action': 'continue',
                'message': colorize("\n❌ Model switching cancelled.", Colors.YELLOW)
            }
        except Exception as e:
            return {
                'action': 'continue',
                'message': colorize(f"❌ Error during model switching: {e}", Colors.BRIGHT_RED)
            }
    
    def _handle_info(self) -> dict:
        """Handle the /info command to show system information."""
        try:
            collection_info = self.chromadb_manager.get_collection_info()
            
            # Get current models from RAG processor if available
            current_generation_model = config.GENERATION_MODEL
            current_embedding_model = config.EMBEDDING_MODEL
            
            if self.rag_processor:
                current_generation_model = getattr(self.rag_processor, 'generation_model', config.GENERATION_MODEL)
                current_embedding_model = getattr(self.rag_processor, 'embedding_model', config.EMBEDDING_MODEL)
            
            info_lines = [
                colorize("🔧 System Information", Colors.BRIGHT_CYAN, Colors.BOLD),
                colorize("=" * 25, Colors.CYAN),
                colorize("📁 ChromaDB Path: ", Colors.BRIGHT_BLUE) + colorize(str(collection_info.get('db_path', 'Unknown')), Colors.WHITE),
                colorize("📦 Collection Name: ", Colors.BRIGHT_BLUE) + colorize(str(collection_info.get('name', 'Unknown')), Colors.WHITE),
                colorize("📊 Document Count: ", Colors.BRIGHT_BLUE) + colorize(str(collection_info.get('count', 'Unknown')), Colors.BRIGHT_WHITE),
                colorize("🧠 Embedding Model: ", Colors.BRIGHT_GREEN) + colorize(current_embedding_model, Colors.WHITE),
                colorize("🤖 Generation Model: ", Colors.BRIGHT_GREEN) + colorize(current_generation_model, Colors.BRIGHT_CYAN),
                colorize("🔤 Sentence Transformer: ", Colors.BRIGHT_GREEN) + colorize(config.SENTENCE_TRANSFORMER_MODEL, Colors.WHITE),
                colorize("🐛 Debug Mode: ", Colors.BRIGHT_YELLOW) + colorize(str(config.DEBUG_MODE), Colors.WHITE),
                colorize("📝 Verbose Logging: ", Colors.BRIGHT_YELLOW) + colorize(str(config.VERBOSE_LOGGING), Colors.WHITE)
            ]
            
            if "error" in collection_info:
                info_lines.append(colorize(f"❌ Collection Error: {collection_info['error']}", Colors.BRIGHT_RED))
            
            return {
                'action': 'continue',
                'message': '\n'.join(info_lines)
            }
            
        except Exception as e:
            return {
                'action': 'continue',
                'message': colorize(f"❌ Error getting system information: {e}", Colors.BRIGHT_RED)
            }
    
    def get_available_commands(self) -> list:
        """
        Get list of available commands.
        
        Returns:
            list: List of available command names
        """
        return list(self.commands.keys())
    
    def print_startup_help(self):
        """Print startup help message."""
        print_header("\n🚀 RAG Interactive Mode")
        print_subheader("Available commands:")
        print(colorize("  /bye     ", Colors.BRIGHT_MAGENTA) + colorize("- Exit the program", Colors.WHITE))
        print(colorize("  /context ", Colors.BRIGHT_MAGENTA) + colorize("- Add multi-line context to ChromaDB", Colors.WHITE))
        print(colorize("  /clear   ", Colors.BRIGHT_MAGENTA) + colorize("- Clear all documents from ChromaDB", Colors.WHITE))
        print(colorize("  /model   ", Colors.BRIGHT_MAGENTA) + colorize("- Switch LLM model (gemma3:4b/llama3.2)", Colors.WHITE))
        print(colorize("  /info    ", Colors.BRIGHT_MAGENTA) + colorize("- Show system information", Colors.WHITE))
        print(colorize("  /help    ", Colors.BRIGHT_MAGENTA) + colorize("- Show this help message", Colors.WHITE))
        print_info("Enter your queries or use commands above.")
        
        if config.DEBUG_MODE:
            print_dim(f"Using embedding model: {config.EMBEDDING_MODEL}")
            print_dim(f"Using generation model: {config.GENERATION_MODEL}")
