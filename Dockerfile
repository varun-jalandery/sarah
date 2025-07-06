FROM ollama/ollama:latest

WORKDIR /app

# Copy your Python application files
COPY . .

# Install Python and dependencies
RUN apt-get update && apt-get install -y python3 python3-pip
RUN python3 -m pip install -r requirements.txt
RUN python3 -m ven .venv
# Make the startup script executable
COPY start.sh .
RUN chmod +x start.sh

# Expose the Ollama API port
EXPOSE 11434

# Run the startup script
CMD ["./start.sh"]
