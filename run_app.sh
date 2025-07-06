#!/bin/bash
# Disable ChromaDB telemetry to avoid capture() error
export ANONYMIZED_TELEMETRY=False
export CHROMA_TELEMETRY_DISABLED=1

# Run the application
python app.py
