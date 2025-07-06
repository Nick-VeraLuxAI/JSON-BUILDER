import argparse
import subprocess
import sys

def run_dataset_builder(count):
    print(f"🛠️ Running dataset builder for {count} entries...")
    result = subprocess.run(
        [sys.executable, "make_dataset.py", "--count", str(count)],
        check=False
    )
    if result.returncode != 0:
        print("❌ Dataset build failed.")
        exit(1)
    print("🎉 Dataset build complete.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=20000, help="How many samples to generate")
    args = parser.parse_args()

    # Server should already be running (launched from .bat)
    print("🔗 Assuming LLaMA server is already running on localhost:8080")
    run_dataset_builder(args.count)

if __name__ == "__main__":
    main()
