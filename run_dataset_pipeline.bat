@echo off
setlocal

REM === CONFIG ===
set "MODEL_FILE=C:\Users\ndesantis\Documents\GitHub\JSON-BUILDER\Meta-Llama-3-8B-Instruct.Q6_K.gguf"
set "SERVER_PORT=8080"
set "COUNT=20000"
set "THREADS=20"
set "OUTPUT=batch_raw.jsonl"
set "VALIDATED=batch_clean.jsonl"
set "FINAL=legendary_dataset.jsonl"
set "LLAMA_EXE=llama-server.exe"

REM === STEP 0: Kill existing server if needed ===
echo ≡ƒö¬ Checking for any process using port %SERVER_PORT%...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":%SERVER_PORT%" ^| find "LISTENING"') do (
    echo ⚠️ Port %SERVER_PORT% in use by PID %%a, terminating...
    taskkill /F /PID %%a >nul 2>&1
)

REM === STEP 1: Start fast llama-server.exe ===
echo [1/4] Starting LLaMA HTTP server...
start "LLaMA Server" cmd /k %LLAMA_EXE% --model "%MODEL_FILE%" --port %SERVER_PORT% --threads %THREADS% --ctx-size 4096 --n-gpu-layers 100

REM === STEP 2: Wait for server to warm up ===
echo ΓÅ│ Waiting 15s for LLaMA to initialize...
timeout /t 15 >nul

REM === STEP 3: Run dataset builder ===
echo [2/4] Running full memory dataset pipeline...
python run_full_pipeline.py --count %COUNT%

REM === DONE ===
echo Γ£à All done. Press any key to exit.
pause
