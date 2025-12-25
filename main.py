import requests
import concurrent.futures
import os
import time
import threading

# ============== CONFIG =================
API_URL = "https://ark.ap-southeast.bytepluses.com/api/v3/chat/completions"
API_KEY = os.getenv("ARK_API_KEY")

MODEL = "seed-1-6-flash-250715"

TARGET_TOKENS = 20_000_000
RUN_SECONDS = 3600  # 1 hour

REQUEST_INTERVAL = 16     # seconds between requests
CONCURRENCY = 3           # safe & stable

# ======================================
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

prompt = (
    "Write an extremely long, highly detailed technical essay about "
    "AI systems, scaling laws, training infrastructure, inference optimization, "
    "safety, alignment, economics, and future research directions."
)

payload = {
    "model": MODEL,
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 100000,
}

lock = threading.Lock()
total_tokens = 0
start_time = time.time()

# ======================================
def call_seed16(i):
    global total_tokens
    try:
        r = requests.post(API_URL, headers=headers, json=payload, timeout=180)
        data = r.json()
        usage = data.get("usage", {}).get("total_tokens", 0)

        with lock:
            total_tokens += usage
            elapsed = time.time() - start_time
            tpm = int(total_tokens / elapsed * 60)

        print(
            f"[Req {i}] +{usage:,} tokens | "
            f"Total={total_tokens:,} | TPM≈{tpm:,}"
        )
    except Exception as e:
        print(f"[Req {i}] ❌ {e}")

# ======================================
def run_load():
    i = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        while True:
            elapsed = time.time() - start_time

            if elapsed >= RUN_SECONDS:
                print("⏱ 1 hour reached")
                break

            if total_tokens >= TARGET_TOKENS:
                print("🎯 20M tokens reached")
                break

            executor.submit(call_seed16, i)
            i += 1
            time.sleep(REQUEST_INTERVAL)

    print("\n✅ DONE")
    print(f"🔥 Total tokens: {total_tokens:,}")
    print(f"⏱ Runtime: {int((time.time()-start_time)/60)} minutes")

# ======================================
if __name__ == "__main__":
    run_load()
