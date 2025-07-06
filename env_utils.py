#!/usr/bin/env python3
"""
Environment utilities for MyAI project.
Provides helper functions for managing environment variables and configuration.
"""

import os
import shutil
from config import config

def create_env_from_example():
    """Create .env file from .env.example if it doesn't exist."""
    env_path = '.env'
    example_path = '.env.example'
    
    if os.path.exists(env_path):
        print(f"✓ {env_path} already exists")
        return
    
    if os.path.exists(example_path):
        shutil.copy2(example_path, env_path)
        print(f"✓ Created {env_path} from {example_path}")
        print("  Please review and modify the values as needed.")
    else:
        print(f"✗ {example_path} not found")

def validate_config():
    """Validate that all required configuration values are set."""
    print("=== Configuration Validation ===")
    
    required_configs = [
        'CHROMA_DB_PATH',
        'COLLECTION_NAME',
        'EMBEDDING_MODEL',
        'GENERATION_MODEL',
        'SENTENCE_TRANSFORMER_MODEL',
        'DEFAULT_FILE_PATH'
    ]
    
    all_valid = True
    
    for config_name in required_configs:
        value = getattr(config, config_name, None)
        if value:
            print(f"✓ {config_name}: {value}")
        else:
            print(f"✗ {config_name}: Not set or empty")
            all_valid = False
    
    if all_valid:
        print("\n✓ All required configurations are set!")
    else:
        print("\n✗ Some required configurations are missing!")
    
    return all_valid

def check_file_paths():
    """Check if configured file paths exist."""
    print("\n=== File Path Validation ===")
    
    # Check default file path
    if os.path.exists(config.DEFAULT_FILE_PATH):
        print(f"✓ Default file exists: {config.DEFAULT_FILE_PATH}")
    else:
        print(f"✗ Default file not found: {config.DEFAULT_FILE_PATH}")
    
    # Check ChromaDB path
    if os.path.exists(config.CHROMA_DB_PATH):
        print(f"✓ ChromaDB path exists: {config.CHROMA_DB_PATH}")
    else:
        print(f"⚠ ChromaDB path doesn't exist (will be created): {config.CHROMA_DB_PATH}")

def print_environment_status():
    """Print comprehensive environment status."""
    print("=== MyAI Environment Status ===")
    
    # Check .env file
    if os.path.exists('.env'):
        print("✓ .env file exists")
    else:
        print("✗ .env file not found")
    
    # Validate configuration
    validate_config()
    
    # Check file paths
    check_file_paths()
    
    # Print current config
    print("\n=== Current Configuration ===")
    config.print_config()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "init":
            create_env_from_example()
        elif command == "validate":
            validate_config()
        elif command == "check":
            check_file_paths()
        elif command == "status":
            print_environment_status()
        else:
            print("Available commands:")
            print("  init     - Create .env from .env.example")
            print("  validate - Validate configuration")
            print("  check    - Check file paths")
            print("  status   - Show complete environment status")
    else:
        print_environment_status()
