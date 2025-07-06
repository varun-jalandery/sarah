"""
Configuration module for MyAI project.
Loads environment variables from .env file and provides default values.
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class that loads settings from environment variables."""
    
    # ChromaDB Configuration
    CHROMA_DB_PATH: str = os.getenv('CHROMA_DB_PATH', './chroma_db')
    COLLECTION_NAME: str = os.getenv('COLLECTION_NAME', 'docs_with_mxbai_embed')
    
    # Ollama Models Configuration
    EMBEDDING_MODEL: str = os.getenv('EMBEDDING_MODEL', 'mxbai-embed-large')
    GENERATION_MODEL: str = os.getenv('GENERATION_MODEL', 'llama3.2')
    
    # Sentence Transformer Model
    SENTENCE_TRANSFORMER_MODEL: str = os.getenv('SENTENCE_TRANSFORMER_MODEL', 'BAAI/bge-large-en-v1.5')
    
    # File Processing Configuration
    DEFAULT_FILE_PATH: str = os.getenv('DEFAULT_FILE_PATH', 'context.txt')
    MAX_RETRIEVED_DATA_LENGTH: int = int(os.getenv('MAX_RETRIEVED_DATA_LENGTH', '1000'))
    
    # RAG Configuration
    MAX_RESULTS: int = int(os.getenv('MAX_RESULTS', '1'))
    CONTEXT_WINDOW_SIZE: int = int(os.getenv('CONTEXT_WINDOW_SIZE', '1000'))
    
    # Dynamic Distance Filtering Configuration
    ENABLE_DISTANCE_FILTERING: bool = os.getenv('ENABLE_DISTANCE_FILTERING', 'true').lower() == 'true'
    BASE_DISTANCE_THRESHOLD: float = float(os.getenv('BASE_DISTANCE_THRESHOLD', '0.8'))
    DYNAMIC_THRESHOLD_RATIO: float = float(os.getenv('DYNAMIC_THRESHOLD_RATIO', '0.7'))
    MIN_RESULTS_FOR_FILTERING: int = int(os.getenv('MIN_RESULTS_FOR_FILTERING', '2'))
    FALLBACK_DISTANCE_THRESHOLD: float = float(os.getenv('FALLBACK_DISTANCE_THRESHOLD', '1.0'))
    HARD_DISTANCE_THRESHOLD: float = float(os.getenv('HARD_DISTANCE_THRESHOLD', '1.0'))
    DISTANCE_DEBUG_MODE: bool = os.getenv('DISTANCE_DEBUG_MODE', 'false').lower() == 'true'
    
    # Optional: Ollama Server Configuration
    OLLAMA_HOST: str = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    OLLAMA_TIMEOUT: int = int(os.getenv('OLLAMA_TIMEOUT', '30'))
    
    # Debug Configuration
    DEBUG_MODE: bool = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    VERBOSE_LOGGING: bool = os.getenv('VERBOSE_LOGGING', 'true').lower() == 'true'

    ANONYMIZED_TELEMETRY: bool = os.getenv('ANONYMIZED_TELEMETRY', 'false').lower() == 'true'
    
    @classmethod
    def get_env_info(cls) -> dict:
        """Returns a dictionary of all configuration values."""
        return {
            'CHROMA_DB_PATH': cls.CHROMA_DB_PATH,
            'COLLECTION_NAME': cls.COLLECTION_NAME,
            'EMBEDDING_MODEL': cls.EMBEDDING_MODEL,
            'GENERATION_MODEL': cls.GENERATION_MODEL,
            'SENTENCE_TRANSFORMER_MODEL': cls.SENTENCE_TRANSFORMER_MODEL,
            'DEFAULT_FILE_PATH': cls.DEFAULT_FILE_PATH,
            'MAX_RETRIEVED_DATA_LENGTH': cls.MAX_RETRIEVED_DATA_LENGTH,
            'MAX_RESULTS': cls.MAX_RESULTS,
            'CONTEXT_WINDOW_SIZE': cls.CONTEXT_WINDOW_SIZE,
            'ENABLE_DISTANCE_FILTERING': cls.ENABLE_DISTANCE_FILTERING,
            'BASE_DISTANCE_THRESHOLD': cls.BASE_DISTANCE_THRESHOLD,
            'DYNAMIC_THRESHOLD_RATIO': cls.DYNAMIC_THRESHOLD_RATIO,
            'MIN_RESULTS_FOR_FILTERING': cls.MIN_RESULTS_FOR_FILTERING,
            'FALLBACK_DISTANCE_THRESHOLD': cls.FALLBACK_DISTANCE_THRESHOLD,
            'HARD_DISTANCE_THRESHOLD': cls.HARD_DISTANCE_THRESHOLD,
            'DISTANCE_DEBUG_MODE': cls.DISTANCE_DEBUG_MODE,
            'OLLAMA_HOST': cls.OLLAMA_HOST,
            'OLLAMA_TIMEOUT': cls.OLLAMA_TIMEOUT,
            'DEBUG_MODE': cls.DEBUG_MODE,
            'VERBOSE_LOGGING': cls.VERBOSE_LOGGING,
            'ANONYMIZED_TELEMETRY': cls.ANONYMIZED_TELEMETRY
        }
    
    @classmethod
    def print_config(cls):
        """Prints all configuration values."""
        print("=== MyAI Configuration ===")
        for key, value in cls.get_env_info().items():
            print(f"{key}: {value}")
        print("=" * 27)

# Create a global config instance
config = Config()

def get_config() -> Config:
    """Returns the global configuration instance."""
    return config
