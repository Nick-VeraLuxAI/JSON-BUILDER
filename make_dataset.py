import subprocess
import argparse
import os

def run_command(cmd, label):
    print(f"\n🔧 Running: {label}")
    print(f"➤ {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"❌ {label} failed.\n")
        exit(1)
    print(f"✅ {label} complete.\n")

def main():
    parser = argparse.ArgumentParser(description="Full memory dataset pipeline: generate → validate → merge")
    parser.add_argument("--count", type=int, default=5000, help="Number of samples to generate")
    parser.add_argument("--output", type=str, default="batch_generated.jsonl", help="Name of raw output from generator")
    parser.add_argument("--validated", type=str, default="batch_validated.jsonl", help="Validated output filename")
    parser.add_argument("--merge-with", nargs="*", help="Other .jsonl files to merge with")
    parser.add_argument("--final", type=str, default="memory_dataset_merged.jsonl", help="Final merged dataset filename")
    parser.add_argument("--skip-merge", action="store_true", help="Skip merging step")
    args = parser.parse_args()

    # Step 1: Generate
    run_command(
        ["python", "generate_memories_llama.py", "--count", str(args.count), "--output", args.output],
        "Step 1: Generate"
    )

    # Step 2: Validate
    run_command(
        ["python", "validate_jsonl.py", "--input", args.output, "--output", args.validated],
        "Step 2: Validate"
    )

    # Step 3: Merge (optional)
    if not args.skip_merge:
        merge_inputs = [args.validated] + (args.merge_with if args.merge_with else [])
        run_command(
            ["python", "merge_batches.py", "--input"] + merge_inputs + ["--output", args.final],
            "Step 3: Merge"
        )
    else:
        print("⚠️ Skipping merge step. Validated file is your final output.")

if __name__ == "__main__":
    main()
