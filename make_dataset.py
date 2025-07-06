import subprocess
import argparse
import os
import sys
from datetime import datetime

def run_command(cmd, label):
    print(f"\n🔧 Running: {label}")
    print(f"➤ {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"❌ {label} failed with code {result.returncode}.\n")
        sys.exit(1)
    print(f"✅ {label} complete.\n")

def main():
    parser = argparse.ArgumentParser(description="Full memory dataset pipeline: generate → validate → merge")
    parser.add_argument("--count", type=int, default=5000, help="Number of samples to generate")
    parser.add_argument("--output", type=str, default=None, help="Name of raw output from generator")
    parser.add_argument("--validated", type=str, default=None, help="Validated output filename")
    parser.add_argument("--merge-with", nargs="*", help="Other .jsonl files to merge with")
    parser.add_argument("--final", type=str, default=None, help="Final merged dataset filename")
    parser.add_argument("--skip-merge", action="store_true", help="Skip merging step")
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    raw_output = args.output or f"generated_{timestamp}.jsonl"
    validated_output = args.validated or f"validated_{timestamp}.jsonl"
    merged_output = args.final or f"memory_dataset_{timestamp}.jsonl"

    # Step 1: Generate
    run_command(
        ["python", "generate_memories_llama.py", "--count", str(args.count), "--output", raw_output],
        "Step 1: Generate"
    )

    # Step 2: Validate
    run_command(
        ["python", "validate_jsonl.py", "--input", raw_output, "--output", validated_output],
        "Step 2: Validate"
    )

    # Step 3: Merge (optional)
    if not args.skip_merge:
        merge_inputs = [validated_output] + (args.merge_with if args.merge_with else [])
        run_command(
            ["python", "merge_batches.py", "--input"] + merge_inputs + ["--output", merged_output],
            "Step 3: Merge"
        )
        print(f"\n📦 Final dataset: {merged_output}")
    else:
        print(f"\n⚠️ Skipping merge step. Validated file is your final output: {validated_output}")

if __name__ == "__main__":
    main()
