import json
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

REQUIRED_KEYS = {"action", "type", "subject", "sentiment", "confidence", "original"}
INVALID_LOG_FILE = "invalid_lines.jsonl"

def is_valid_entry(line):
    try:
        entry = json.loads(line.strip())
        if not isinstance(entry, dict):
            return False, line
        if not REQUIRED_KEYS.issubset(entry.keys()):
            return False, line
        if entry["action"] != "remember":
            return False, line
        if not isinstance(entry["type"], str):
            return False, line
        if not isinstance(entry["subject"], str):
            return False, line
        if not isinstance(entry["sentiment"], str):
            return False, line
        if not isinstance(entry["confidence"], (float, int)):
            return False, line
        if not 0.70 <= float(entry["confidence"]) <= 0.99:
            return False, line
        if not isinstance(entry["original"], str):
            return False, line
        return True, json.dumps(entry)
    except Exception:
        return False, line

def validate_file(input_path, output_path, remove_invalids=True, threads=16):
    with open(input_path, "r", encoding="utf-8") as fin:
        lines = fin.readlines()

    total = len(lines)
    valid_lines = []
    invalid_lines = []

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(is_valid_entry, line): line for line in lines}

        for future in as_completed(futures):
            try:
                is_valid, result = future.result()
                if is_valid:
                    valid_lines.append(result)
                else:
                    invalid_lines.append(result.strip())
            except Exception:
                invalid_lines.append(futures[future].strip())

    valid_count = len(valid_lines)
    invalid_count = len(invalid_lines)

    print(f"\n📊 Validation Summary:")
    print(f"  Total lines:       {total}")
    print(f"  ✅ Valid:           {valid_count}")
    print(f"  ❌ Invalid:         {invalid_count}")
    print(f"  🎯 Validity Rate:   {round((valid_count / total) * 100, 2) if total else 0}%")

    if remove_invalids:
        with open(output_path, "w", encoding="utf-8") as fout:
            fout.write("\n".join(valid_lines))
        print(f"🧹 Cleaned output written to: {output_path}")

        if invalid_lines:
            with open(INVALID_LOG_FILE, "w", encoding="utf-8") as flog:
                flog.write("\n".join(invalid_lines))
            print(f"🚫 Invalid lines saved to: {INVALID_LOG_FILE}")
    else:
        print("🟡 No files written (remove_invalids=False)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="legendary_memories_mixtral.jsonl", help="Input .jsonl file")
    parser.add_argument("--output", type=str, default="validated_memories.jsonl", help="Output validated .jsonl file")
    parser.add_argument("--keep-invalids", action="store_true", help="Keep invalid entries (no cleanup)")
    parser.add_argument("--threads", type=int, default=16, help="Number of parallel threads")
    args = parser.parse_args()

    validate_file(args.input, args.output, remove_invalids=not args.keep_invalids, threads=args.threads)
