import json

# === Config ===
INPUT_FILE = "legendary_memories_mixtral.jsonl"
OUTPUT_FILE = "validated_memories.jsonl"
REQUIRED_KEYS = {"action", "type", "subject", "sentiment", "confidence", "original"}
REMOVE_INVALIDS = True  # Set to False if you only want to see a report

def is_valid_entry(entry):
    # Must be a dict
    if not isinstance(entry, dict):
        return False
    # Must contain all keys
    if not REQUIRED_KEYS.issubset(entry.keys()):
        return False
    # Field types
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

def validate_file():
    total = 0
    valid = 0
    invalid = 0

    with open(INPUT_FILE, "r", encoding="utf-8") as fin:
        lines = fin.readlines()

    output_lines = []

    for line in lines:
        total += 1
        try:
            data = json.loads(line.strip())
            if is_valid_entry(data):
                valid += 1
                output_lines.append(json.dumps(data))
            else:
                invalid += 1
        except Exception as e:
            invalid += 1

    print(f"\n📊 Validation Summary:")
    print(f"  Total lines:   {total}")
    print(f"  ✅ Valid:       {valid}")
    print(f"  ❌ Invalid:     {invalid}")

    if REMOVE_INVALIDS:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as fout:
            fout.write("\n".join(output_lines))
        print(f"\n🧹 Cleaned output written to: {OUTPUT_FILE}")
    else:
        print("No output file written (REMOVE_INVALIDS=False)")

if __name__ == "__main__":
    validate_file()
