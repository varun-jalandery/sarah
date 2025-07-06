#!/bin/sh

# Start Ollama in the background
ollama serve &

# Wait for Ollama to start
sleep 5

# Pull the required model(s)
ollama pull llama3.2:latest

# Start your Python application
source .venv/bin/activate
sh ./run_app.sh