#!/bin/bash

echo "📦 Installing dependencies..."
apt update && apt install -y git build-essential wget curl python3 python3-pip

echo "🐍 Installing Python packages..."
pip3 install -r requirements.txt || pip3 install argparse requests

echo "📥 Cloning llama.cpp..."
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

echo "⚙️ Building llama.cpp with server + CUDA support..."
make LLAMA_CUBLAS=1 LLAMA_SERVER=1 -j $(nproc)

echo "📂 Preparing model directory..."
mkdir -p models/meta-llama-3
cd models/meta-llama-3

echo "⬇️ Downloading LLaMA 3 8B Instruct Q6_K model..."
wget https://huggingface.co/RichardErkhov/NousResearch_-_Meta-Llama-3-8B-Instruct-gguf/resolve/main/Meta-Llama-3-8B-Instruct.Q6_K.gguf -O Meta-Llama-3-8B-Instruct.Q6_K.gguf

cd ../../../

echo "🚀 Launching 4 llama servers in background..."
./llama.cpp/server --model ./llama.cpp/models/meta-llama-3/Meta-Llama-3-8B-Instruct.Q6_K.gguf --port 8080 --n_gpu_layers 100 --ctx-size 4096 --threads $(nproc) &
./llama.cpp/server --model ./llama.cpp/models/meta-llama-3/Meta-Llama-3-8B-Instruct.Q6_K.gguf --port 8081 --n_gpu_layers 100 --ctx-size 4096 --threads $(nproc) &
./llama.cpp/server --model ./llama.cpp/models/meta-llama-3/Meta-Llama-3-8B-Instruct.Q6_K.gguf --port 8082 --n_gpu_layers 100 --ctx-size 4096 --threads $(nproc) &
./llama.cpp/server --model ./llama.cpp/models/meta-llama-3/Meta-Llama-3-8B-Instruct.Q6_K.gguf --port 8083 --n_gpu_layers 100 --ctx-size 4096 --threads $(nproc) &

sleep 10
echo "⏳ Waiting for servers to finish loading..."

echo "📂 Copying source code into working directory..."
mkdir -p pipeline
cp generate_memories_llama.py run_full_pipeline.py validate_jsonl.py merge_batches.py pipeline/

cd pipeline

echo "🧠 Running full memory dataset pipeline..."
python3 run_full_pipeline.py --count 50000 --output batch_generated.jsonl --validated batch_validated.jsonl --final memory_dataset_merged.jsonl

echo "✅ All steps completed successfully!"

 
