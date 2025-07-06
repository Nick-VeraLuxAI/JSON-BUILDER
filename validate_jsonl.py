import json
import argparse

# === Default Config ===
DEFAULT_INPUT_FILE = "legendary_memories_mixtral.jsonl"
DEFAULT_OUTPUT_FILE = "validated_memories.jsonl"
INVALID_LOG_FILE = "invalid_lines.jsonl"
REQUIRED_KEYS = {"action", "type", "subject", "sentiment", "confidence", "original"}

def is_valid_entry(entry):
    try:
        if not isinstance(entry, dict):
            return False
        if not REQUIRED_KEYS.issubset(entry.keys()):
            return False
        if entry["action"] != "remember":
            return False
        if not isinstance(entry["type"], str):
            return False
        if not isinstance(entry["subject"], str):
            return False
        if not isinstance(entry["sentiment"], str):
            return False
        if not isinstance(entry["confidence"], (float, int)):
            return False
        if not 0.70 <= float(entry["confidence"]) <= 0.99:
            return False
        if not isinstance(entry["original"], str):
            return False
        return True
    except Exception:
        return False

def validate_file(input_file, output_file, remove_invalids=True):
    total = 0
    valid = 0
    invalid = 0
    valid_lines = []
    invalid_lines = []

    with open(input_file, "r", encoding="utf-8") as fin:
        for line in fin:
            total += 1
            try:
                data = json.loads(line.strip())
                if is_valid_entry(data):
                    valid += 1
                    valid_lines.append(json.dumps(data))
                else:
                    invalid += 1
                    invalid_lines.append(line.strip())
            except Exception:
                invalid += 1
                invalid_lines.append(line.strip())

    print(f"\n📊 Validation Summary:")
    print(f"  Total lines:       {total}")
    print(f"  ✅ Valid:           {valid}")
    print(f"  ❌ Invalid:         {invalid}")
    print(f"  🎯 Validity Rate:   {round((valid / total) * 100, 2) if total else 0}%")

    if remove_invalids:
        with open(output_file, "w", encoding="utf-8") as fout:
            fout.write("\n".join(valid_lines))
        print(f"🧹 Cleaned output written to: {output_file}")

        if invalid_lines:
            with open(INVALID_LOG_FILE, "w", encoding="utf-8") as flog:
                flog.write("\n".join(invalid_lines))
            print(f"🚫 Invalid lines saved to: {INVALID_LOG_FILE}")
    else:
        print("🟡 No files written (remove_invalids=False)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default=DEFAULT_INPUT_FILE, help="Path to input .jsonl file")
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT_FILE, help="Path to output cleaned .jsonl file")
    parser.add_argument("--keep-invalids", action="store_true", help="Keep invalid entries (no cleanup)")
    args = parser.parse_args()

    validate_file(args.input, args.output, remove_invalids=not args.keep_invalids)
