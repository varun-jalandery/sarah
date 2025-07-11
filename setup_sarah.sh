sudo apt-get update &&
sudo apt -y install unzip  &&
sudo apt -y install python3  &&
sudo apt -y install python3.10-venv  &&
curl -fsSL https://ollama.com/install.sh | sh  &&
echo "Sleeping for 5 seconds, let Ollama wake up" &&
sleep 5 &&
ollama pull mistral:7b &&
# ollama pull gemma3:4b  &&
# ollama pull gemma3:27b &&
# ollama pull gemma3n:e4b &&
wget https://github.com/varun-jalandery/sarah/archive/refs/heads/mainline.zip  &&
unzip mainline.zip  &&
cd sarah-mainline  &&
python3 -m venv .venv  &&
source .venv/bin/activate && 
python -m pip install -r requirements.txt &&
echo "to run the app type the command : cd sarah-mainline && ./run_app.sh"
