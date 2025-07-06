import json
import random
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import argparse
from datetime import datetime

API_URLS = [
    "http://localhost:8080/v1/chat/completions",
    "http://localhost:8081/v1/chat/completions",
    "http://localhost:8082/v1/chat/completions",
    "http://localhost:8083/v1/chat/completions"
]

HEADERS = {"Content-Type": "application/json"}
MAX_RETRIES = 3

DEFAULT_PROMPT = """You are a helpful assistant storing realistic memories. Create a memory like a real user might say to you in casual conversation.

Format: {
  "action": "remember",
  "type": "preference" | "fact" | "observation",
  "subject": "<2–4 word summary of topic>",
  "sentiment": "positive" | "neutral" | "negative" | "mixed",
  "confidence": <float between 0.70 and 0.99>,
  "original": "<natural human phrasing>"
}

Respond with just the JSON. No markdown. No explanation."""

def generate_entry(prompt_template):
    payload = {
        "messages": [{"role": "user", "content": prompt_template}],
        "temperature": 0.9,
        "max_tokens": 300
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            url = random.choice(API_URLS)  # Randomly distribute load
            response = requests.post(url, json=payload, headers=HEADERS, timeout=60)

            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"].strip()
                try:
                    json.loads(content)  # Validate JSON
                    return content
                except json.JSONDecodeError:
                    print(f"⚠️ Invalid JSON (attempt {attempt}): {content[:100]}...", flush=True)
            else:
                print(f"❌ HTTP {response.status_code} from {url}: {response.text[:100]}", flush=True)
        except Exception as e:
            print(f"⚠️ Exception on attempt {attempt} to {url}: {e}", flush=True)
        time.sleep(0.5 + random.uniform(0, 0.5))  # Shorter backoff on powerful GPUs
    return None

def main():
    parser = argparse.ArgumentParser(description="Parallel memory generation via local LLaMA model")
    parser.add_argument("--count", type=int, default=2000, help="Number of memories to generate")
    parser.add_argument("--output", type=str, help="Output .jsonl filename")
    parser.add_argument("--threads", type=int, default=10, help="Number of parallel threads")
    parser.add_argument("--prompt", type=str, help="Optional path to custom prompt.txt")
    args = parser.parse_args()

    # Load custom prompt if provided
    if args.prompt and os.path.exists(args.prompt):
        with open(args.prompt, "r", encoding="utf-8") as f:
            prompt_template = f.read()
    else:
        prompt_template = DEFAULT_PROMPT

    # Set output name with timestamp fallback
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"memories_{timestamp}.jsonl"

    total = args.count
    print(f"\n🔁 Generating {total} entries using {args.threads} threads across 4 GPUs...")
    print(f"💾 Output: {args.output}\n")

    with open(args.output, "w", encoding="utf-8") as f_out:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            futures = [executor.submit(generate_entry, prompt_template) for _ in range(total)]

            for i, future in enumerate(as_completed(futures), 1):
                result = future.result()
                if result:
                    f_out.write(result + "\n")
                    print(f"[{i}/{total}] ✅", flush=True)
                else:
                    print(f"[{i}/{total}] ❌ Failed after retries", flush=True)

    print(f"\n✅ Done. Saved results to: {args.output}")

if __name__ == "__main__":
    main()

