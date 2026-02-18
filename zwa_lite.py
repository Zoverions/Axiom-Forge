import json
import re
import sys
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# --- CONFIGURATION (The "Zero-Weight" Stack) ---
MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"
CONSTELLATION_FILE = "constellation.json"
WHITELIST = {'requests', 're', 'math', 'datetime', 'json', 'random'}

# --- CORE 1: THE BRAIN (4-Bit Quantized Load) ---
print(f"Loading Z-Core ({MODEL_ID})...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    trust_remote_code=True,
    device_map="auto",
    torch_dtype=torch.float16,
    load_in_4bit=True # Requires bitsandbytes; fails gracefully to CPU if missing
)
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

# --- CORE 2: THE MEMORY (JSON Constellation) ---
constellation = {}
if os.path.exists(CONSTELLATION_FILE):
    with open(CONSTELLATION_FILE, 'r') as f: constellation = json.load(f)

def save_skill(goal, code):
    sid = goal.lower().replace(" ", "_")[:35]
    constellation[sid] = {"desc": goal, "code": code}
    with open(CONSTELLATION_FILE, 'w') as f: json.dump(constellation, f)
    print(f"\n[✨] Crystallized: {sid}")

def find_skill(query):
    # Keyword match + length check to avoid false positives on short words
    q_words = [w.lower() for w in query.split() if len(w) > 3]
    for sid, data in constellation.items():
        if any(w in data['desc'].lower() for w in q_words): return data
    return None

# --- CORE 3: THE SAFETY (Regex Firewall) ---
def validate(code):
    if re.search(r'\b(os\.system|subprocess|exec|eval|open\s*\(.*,\s*[\'"]w[\'"]\))\b', code):
        return False, "Banned syscall/write detected."
    imports = re.findall(r'import (\w+)|from (\w+)', code)
    for i in [x for t in imports for x in t if x]:
        if i not in WHITELIST: return False, f"Illegal import: {i}"
    return True, "Safe"

# --- CORE 4: THE LOOP (Infer -> Build -> Run) ---
def run(query):
    # 1. Search
    skill = find_skill(query)

    if skill:
        print(f"[⚡] JIT Loading: {skill['desc']}")
        code = skill['code']
    else:
        print("[🔧] Building Tool...")
        messages = [{"role": "user", "content": (
            f"Write a Python script to: {query}.\n"
            f"Constraints: Define `def execute():` returning a string. Use ONLY: {', '.join(WHITELIST)}.\n"
            f"Output **only** the code inside a ```python block."
        )}]
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

        out = pipe(prompt, max_new_tokens=300, do_sample=False)[0]['generated_text']
        code_match = re.search(r'```python\n(.*?)```', out, re.DOTALL)
        if not code_match: return "Error: Model failed to generate code."
        code = code_match.group(1)

    # 2. Validate
    valid, msg = validate(code)
    if not valid: return f"[⛔] Safety Block: {msg}"

    # 3. Execute
    sandbox = {m: __import__(m) for m in WHITELIST}
    local = {}
    try:
        exec(code, sandbox, local)
        # Robust entry point check
        entry = local.get('execute', local.get('execute_task'))
        if not entry: return "Error: No `execute()` function found."

        res = str(entry())

        # 4. Automate (Crystallize on Success)
        if not skill and "Error" not in res and len(res) > 5: save_skill(query, code)
        return res
    except Exception as e: return f"Runtime Error: {e}"

# --- BOOTSTRAP SEQUENCE ---
if not constellation:
    print("Empty Constellation detected. Bootstrapping Genesis Tools...")
    genesis = [
        "fetch website html using requests",
        "clean html tags using re",
        "get current utc date using datetime"
    ]
    for g in genesis:
        print(f"Genesis: {g}")
        run(g)

# --- CLI INTERFACE ---
if __name__ == "__main__":
    print(f"ZWA Lite v2.1 // Skills: {len(constellation)}")
    print("Type 'exit' to quit.")
    while True:
        try:
            q = input("\nZ-Core> ")
            if q.lower() in ['exit', 'quit']: break
            if not q.strip(): continue
            print(f"Output: {run(q)}")
        except KeyboardInterrupt: break
