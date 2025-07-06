import json
import random
import time
import requests
import argparse

# === CONFIG ===
API_URL = "http://localhost:8080/completions"
DEFAULT_OUTPUT_FILE = "legendary_memories_mixtral.jsonl"
DEFAULT_TOTAL_ENTRIES = 20000  # fallback if --count not provided

# Fields for variety
TYPE_WEIGHTS = {"preference": 0.4, "fact": 0.35, "observation": 0.25}
SENTIMENT_POOL = ["positive", "neutral", "negative", "mixed"]

# Prompt template for Mixtral
PROMPT_TPL = """
You are a JSON generator for an AI memory system. Generate one JSON object with:
action: "remember"
type: "{type}"
subject: "<short 2–4 word summary>"
sentiment: "{sentiment}"
confidence: <number between 0.70 and 0.99>
original: "<a realistic human statement>"

Return ONLY the JSON object, no extra text.
"""

HEADERS = {"Content-Type": "application/json"}

def build_payload(entry_type, sentiment):
    prompt = PROMPT_TPL.format(type=entry_type, sentiment=sentiment)
    return {
        "model": "mixtral-8x7b-instruct",
        "prompt": prompt,
        "max_tokens": 120,
        "temperature": 0.9,
        "stop": ["}", "\""]  # Improved stop sequence
    }

def generate_one():
    entry_type = random.choices(list(TYPE_WEIGHTS), weights=TYPE_WEIGHTS.values())[0]
    sentiment = random.choice(SENTIMENT_POOL)
    payload = build_payload(entry_type, sentiment)

    try:
        resp = requests.post(API_URL, json=payload, headers=HEADERS)
        resp.raise_for_status()
        txt = resp.json()["choices"][0]["text"].strip()

        if not txt.endswith("}"):
            txt += "}"

        try:
            return json.loads(txt)
        except json.JSONDecodeError as e:
            print(f"❌ JSON error: {e}\n⤵️ Raw output:\n{txt}\n")
            with open("failed_outputs.log", "a", encoding="utf-8") as log:
                log.write(txt + "\n")
            return None

    except Exception as e:
        print(f"🚨 API Error: {e}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=DEFAULT_TOTAL_ENTRIES, help="Number of entries to generate")
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT_FILE, help="Output .jsonl filename")
    args = parser.parse_args()

    start_time = time.time()
    count = 0

    with open(args.output, "w", encoding="utf-8") as fout:
        while count < args.count:
            entry = generate_one()
            if entry and set(entry.keys()) >= {"action", "type", "subject", "sentiment", "confidence", "original"}:
                fout.write(json.dumps(entry) + "\n")
                count += 1
                if count % 500 == 0:
                    print(f"✅ {count} entries written.")
            else:
                print("⚠️ Invalid or missing fields. Retrying...")

            time.sleep(0.1)  # Rate limiting safety

    elapsed = round(time.time() - start_time, 2)
    print(f"\n🎉 Done! Generated {args.count} entries in {elapsed} seconds.")
    print(f"📝 Output written to: {args.output}")

if __name__ == "__main__":
    main()
