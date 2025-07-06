RUN THESE COMMANDS IN THE TERMINAL WINDOW:

Install Python deps:
pip install requests

Launch Mixtral 8×7B via llama.cpp HTTP:
python server.py --model mixtral-8x7b-instruct.gguf --port 8080

Run the generator:
python generate_memories_mixtral.py



