import json
import argparse
from pathlib import Path

REQUIRED_KEYS = {"action", "type", "subject", "sentiment", "confidence", "original"}

def is_valid_entry(entry):
    return (
        isinstance(entry, dict)
        and REQUIRED_KEYS.issubset(entry.keys())
        and isinstance(entry["type"], str)
        and isinstance(entry["subject"], str)
        and isinstance(entry["sentiment"], str)
        and isinstance(entry["original"], str)
        and isinstance(entry["confidence"], (float, int))
        and entry["action"] == "remember"
        and 0.70 <= float(entry["confidence"]) <= 0.99
    )

def merge_jsonl(files, output_file, validate=True, dedupe=True):
    seen = set()
    merged = []

    for file in files:
        print(f"🔄 Loading: {file}")
        with open(file, "r", encoding="utf-8") as fin:
            for line in fin:
                line = line.strip()
                try:
                    entry = json.loads(line)
                    if validate and not is_valid_entry(entry):
                        continue
                    if dedupe:
                        key = json.dumps(entry, sort_keys=True)
                        if key in seen:
                            continue
                        seen.add(key)
                    merged.append(entry)
                except json.JSONDecodeError:
                    continue

    with open(output_file, "w", encoding="utf-8") as fout:
        for item in merged:
            fout.write(json.dumps(item) + "\n")

    print(f"\n✅ Merged {len(merged)} unique valid entries to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge multiple .jsonl memory datasets into one")
    parser.add_argument("--input", nargs="+", required=True, help="List of .jsonl input files")
    parser.add_argument("--output", type=str, default="merged_memories.jsonl", help="Merged output file")
    parser.add_argument("--no-validate", action="store_true", help="Skip validation checks")
    parser.add_argument("--no-dedupe", action="store_true", help="Allow duplicates")
    args = parser.parse_args()

    merge_jsonl(
        files=args.input,
        output_file=args.output,
        validate=not args.no_validate,
        dedupe=not args.no_dedupe
    )
