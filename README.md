# Sarah

A Python-based AI application leveraging LLM models, Ollama, vector embeddings, and ChromaDb to store
the embeddings for serving context to the LLM before replying to prompts.

## ✨ Enhanced Formatting Features

Your MyAI application features enhanced formatting capabilities for AI responses:

- **Enhanced Bold Text**: More prominent and visually striking bold formatting
- **Elegant Italic Text**: Beautiful italic styling for definitions and subtle emphasis  
- **Combined Emphasis**: ***Bold italic*** text for critical information
- **Multiple Styles**: Support for underlined, strikethrough, and highlighted text
- **Better Code Display**: Enhanced inline code formatting with improved visibility
- **Visual Hierarchy**: Different emphasis levels create clear information structure

### Formatting Options

- **Bold text** - `**text**` for important concepts and key terms
- *Italic text* - `*text*` for definitions and subtle emphasis  
- ***Bold italic text*** - `***text***` for critical information
- __Underlined bold__ - `__text__` for strong emphasis with underline
- _Underlined italic_ - `_text_` for elegant emphasis with underline
- ~~Strikethrough text~~ - `~~text~~` for corrections or deprecated info
- `Enhanced inline code` - `` `code` `` for technical terms and commands
- ==Highlighted text== - `==text==` for warnings and special notes

## Tools Used

1. **Ollama** - https://ollama.com/
   - Download Ollama installer from https://ollama.com/ and set it up as per GUI instructions from the installer during setup
   - The end result is that you should have ollama command executable on your command line tool

## Overview

This project is an AI/ML application that combines various technologies including:
- Vector database storage with ChromaDB
- Sentence embeddings with sentence-transformers
- Local LLM integration with Ollama
- Environment-based configuration with python-dotenv

## Features

- **Vector Database**: ChromaDB integration for efficient similarity search and retrieval
- **Sentence Embeddings**: Generate and work with semantic text representations
- **Local LLM**: Ollama integration for local language model inference
- **Environment Configuration**: Flexible configuration using .env files
- **RAG Pipeline**: Retrieval-Augmented Generation for enhanced responses
- **Dynamic Distance Filtering**: Advanced filtering system that improves retrieval accuracy by filtering results based on semantic similarity distances

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Ollama installed and running

## Installation

1. Clone the repository:
```bash
git clone github.com:varun-jalandery/myai.git
cd myai
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment configuration:
```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your preferred settings
nano .env  # or use your preferred editor
```

## Configuration

The application uses environment variables for configuration. Key settings include:

### ChromaDB Configuration
- `CHROMA_DB_PATH`: Path to ChromaDB storage (default: `./chroma_db`)
- `COLLECTION_NAME`: Name of the ChromaDB collection (default: `docs_with_mxbai_embed`)

### Model Configuration
- `EMBEDDING_MODEL`: Ollama model for embeddings (default: `mxbai-embed-large`)
- `GENERATION_MODEL`: Ollama model for text generation (default: `gemma`)
- `SENTENCE_TRANSFORMER_MODEL`: Sentence transformer model (default: `BAAI/bge-large-en-v1.5`)

### File Processing
- `DEFAULT_FILE_PATH`: Default file to process (default: `context.txt`)
- `MAX_RETRIEVED_DATA_LENGTH`: Maximum length of retrieved context (default: `1000`)

### Dynamic Distance Filtering
- `ENABLE_DISTANCE_FILTERING`: Enable/disable distance-based filtering (default: `true`)
- `BASE_DISTANCE_THRESHOLD`: Maximum distance threshold for results (default: `0.8`)
- `DYNAMIC_THRESHOLD_RATIO`: Ratio for dynamic threshold calculation (default: `0.7`)
- `MIN_RESULTS_FOR_FILTERING`: Minimum results needed to apply filtering (default: `2`)
- `FALLBACK_DISTANCE_THRESHOLD`: Fallback threshold when filtering fails (default: `1.0`)
- `DISTANCE_DEBUG_MODE`: Enable detailed distance filtering debug output (default: `false`)

### Debug Options
- `DEBUG_MODE`: Enable debug output (default: `false`)
- `VERBOSE_LOGGING`: Enable verbose logging (default: `true`)

## Usage

### Environment Management
```bash
# Check environment status
python env_utils.py status

# Initialize .env from example
python env_utils.py init

# Validate configuration
python env_utils.py validate
```

### Interactive RAG Mode

```bash
# Start the interactive system
python app.py
```

#### Available Commands
- `/context` - Add multi-line context directly to ChromaDB
- `/clear` - Clear all documents from ChromaDB collection
- `/model` - Switch LLM model between gemma, mistral, and gemma.n
- `/info` - Show system information
- `/help` - Show available commands
- `/bye` - Exit the program

### Programmatic Usage (New Modular System)

```python
from app import RAGApplication

# Initialize the application
app = RAGApplication()
if app.initialize():
    # Add context programmatically
    app.add_context("Your important context here", "source_label")
    
    # Process single queries
    response = app.process_single_query("What is this about?")
    print(response)
    
    # Get system information
    info = app.get_system_info()
    print(f"Documents: {info['collection']['count']}")
    
    # Run interactive mode
    app.run_interactive_mode()
```



#### Adding Context During Interactive Sessions
The `/context` command allows you to add multi-line text directly to your ChromaDB collection:

1. Type `/context` when prompted
2. Enter your multi-line text (paste or type multiple lines)
3. Type `END` on a new line when finished
4. Review the preview and confirm with `y`

Example:
```
Your query: /context

--- Context Input Mode ---
Enter your multi-line context below.
Type 'END' on a new line when finished, or 'CANCEL' to abort.
==================================================
This is important information about my project.
It includes multiple lines and will be stored
as a single document in ChromaDB for future queries.
END

Preview of context to be saved:
------------------------------
This is important information about my project.
It includes multiple lines and will be stored
as a single document in ChromaDB for future queries.
------------------------------
Total length: 156 characters

Save this context to ChromaDB? (y/N): y
✓ Context successfully saved to ChromaDB!
```

#### Clearing ChromaDB Context
You can clear all documents from your ChromaDB collection using the interactive mode:

**Interactive Mode**
```bash
# Within the interactive app.py session
Your query: /clear
```

The clear operation includes safety features:
- Shows current document count before clearing
- Requires confirmation before deletion
- Verifies successful deletion
- Provides detailed feedback

## Dependencies

### Core Dependencies
- **chromadb** (1.0.13) - Vector database for embeddings
- **ollama** (0.5.1) - Local LLM integration
- **sentence-transformers** (4.1.0) - Sentence embeddings
- **python-dotenv** (1.1.1) - Environment variable management

## Project Structure

```
myai/
├── .env                       # Environment configuration (create from .env.example)
├── .env.example              # Example environment configuration
├── config.py                 # Configuration management
├── chromadb_manager.py       # ChromaDB operations and collection management
├── rag_processor.py          # RAG pipeline processing (embeddings, retrieval, generation)
├── enhanced_rag_processor.py # Enhanced RAG processing with formatting
├── interactive_commands.py   # Interactive command handling
├── app.py                   # Main application orchestrator (entry point)
├── env_utils.py             # Environment management utilities
├── enhanced_formatting.py   # Enhanced text formatting capabilities
├── colorful_response_formatter.py # Response formatting with colors
├── colors.py                # Color definitions and utilities
├── requirements.txt         # Python dependencies
└── chroma_db/              # ChromaDB storage directory (auto-created)
```

## Architecture

The project uses a modular architecture with the following components:

- **ChromaDBManager**: Handles all ChromaDB operations and collection management
- **RAGProcessor**: Manages the complete RAG pipeline (embeddings, retrieval, generation)
- **InteractiveCommands**: Handles interactive commands and user input processing
- **RAGApplication**: Main application orchestrator that coordinates all components

## Setup
