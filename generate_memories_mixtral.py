import json
import random
import time
import requests

# === CONFIG ===
API_URL = "http://localhost:8080/completions"
OUTPUT_FILE = "legendary_memories_mixtral.jsonl"
TOTAL_ENTRIES = 20000  # set to 20000–30000 for full dataset

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
        "stop": ["}"]
    }

def generate_one():
    entry_type = random.choices(list(TYPE_WEIGHTS), weights=TYPE_WEIGHTS.values())[0]
    sentiment = random.choice(SENTIMENT_POOL)
    payload = build_payload(entry_type, sentiment)
    resp = requests.post(API_URL, json=payload, headers=HEADERS)
    resp.raise_for_status()
    txt = resp.json()["choices"][0]["text"].strip()
    # Ensure valid JSON
    if not txt.endswith("}"):
        txt = txt + "}"
    return json.loads(txt)

def main():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as fout:
        count = 0
        while count < TOTAL_ENTRIES:
            try:
                entry = generate_one()
                # Basic validation
                if set(entry.keys()) >= {"action","type","subject","sentiment","confidence","original"}:
                    fout.write(json.dumps(entry) + "\n")
                    count += 1
                    if count % 500 == 0:
                        print(f"✅ {count} entries written.")
                else:
                    print("⚠️ Missing keys, retrying...")
            except Exception as e:
                print("🚨 Error:", e)
            time.sleep(0.1)  # Rate limiting safety
    print(f"🎉 Done! Generated {TOTAL_ENTRIES} entries to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
