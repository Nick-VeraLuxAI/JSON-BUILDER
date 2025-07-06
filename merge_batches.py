import json
import argparse
from concurrent.futures import ThreadPoolExecutor
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

def parse_and_filter_lines(lines, validate=True, dedupe=True, seen_set=None):
    results = []
    local_seen = set() if dedupe else None

    for line in lines:
        try:
            entry = json.loads(line.strip())
            if validate and not is_valid_entry(entry):
                continue
            if dedupe:
                key = json.dumps(entry, sort_keys=True)
                if key in seen_set or key in local_seen:
                    continue
                local_seen.add(key)
            results.append(entry)
        except json.JSONDecodeError:
            continue
    return results, local_seen if dedupe else None

def merge_jsonl(files, output_file, validate=True, dedupe=True, threads=16):
    print(f"\n📦 Merging {len(files)} files with validation={validate}, dedupe={dedupe}")

    all_lines = []
    for file in files:
        print(f"🔄 Reading: {file}")
        with open(file, "r", encoding="utf-8") as f:
            all_lines.extend(f.readlines())

    chunk_size = max(1, len(all_lines) // threads)
    chunks = [all_lines[i:i + chunk_size] for i in range(0, len(all_lines), chunk_size)]

    merged = []
    seen = set()

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(parse_and_filter_lines, chunk, validate, dedupe, seen) for chunk in chunks]
        for future in futures:
            results, local_seen = future.result()
            merged.extend(results)
            if dedupe and local_seen:
                seen.update(local_seen)

    with open(output_file, "w", encoding="utf-8") as fout:
        for item in merged:
            fout.write(json.dumps(item) + "\n")

    print(f"\n✅ Merged {len(merged)} entries → {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge multiple .jsonl memory datasets into one")
    parser.add_argument("--input", nargs="+", required=True, help="List of .jsonl input files")
    parser.add_argument("--output", type=str, default="merged_memories.jsonl", help="Merged output file")
    parser.add_argument("--no-validate", action="store_true", help="Skip validation checks")
    parser.add_argument("--no-dedupe", action="store_true", help="Allow duplicates")
    parser.add_argument("--threads", type=int, default=16, help="Number of threads to use")
    args = parser.parse_args()

    merge_jsonl(
        files=args.input,
        output_file=args.output,
        validate=not args.no_validate,
        dedupe=not args.no_dedupe,
        threads=args.threads
    )

