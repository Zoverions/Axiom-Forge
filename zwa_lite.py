import argparse
import json
import os
import re
from pathlib import Path

MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"
CONSTELLATION_FILE = Path("constellation.json")
WHITELIST = {"requests", "re", "math", "datetime", "json", "random"}
UNSAFE_ACK_ENV = "AXIOM_FORGE_UNSAFE_LOCAL_EXEC"
UNSAFE_ACK_VALUE = "I_UNDERSTAND_THIS_IS_NOT_A_SANDBOX"

_generator = None


def _load_generator():
    """Lazy-load the local model only when a proposal is actually requested."""
    global _generator
    if _generator is not None:
        return _generator

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

    print(f"Loading Z-Core ({MODEL_ID})...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        device_map="auto",
        torch_dtype=torch.float16,
        load_in_4bit=True,
    )
    _generator = (
        tokenizer,
        pipeline("text-generation", model=model, tokenizer=tokenizer),
    )
    return _generator


def _load_constellation():
    if not CONSTELLATION_FILE.exists():
        return {}
    with CONSTELLATION_FILE.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data if isinstance(data, dict) else {}


def _save_constellation(constellation):
    with CONSTELLATION_FILE.open("w", encoding="utf-8") as handle:
        json.dump(constellation, handle, indent=2, sort_keys=True)


def save_skill(constellation, goal, code):
    sid = goal.lower().replace(" ", "_")[:35]
    constellation[sid] = {"desc": goal, "code": code}
    _save_constellation(constellation)
    print(f"\n[research] Stored successful unsafe-local skill: {sid}")


def find_skill(constellation, query):
    q_words = [word.lower() for word in query.split() if len(word) > 3]
    for data in constellation.values():
        description = str(data.get("desc", "")).lower()
        if any(word in description for word in q_words):
            return data
    return None


def lint_generated_code(code):
    """Heuristic lint only. This is explicitly not a security sandbox."""
    blocked_text = re.compile(
        r"\b(os\.system|subprocess|exec|eval|compile|globals|locals|__builtins__|"
        r"getattr|setattr|delattr|open\s*\()\b"
    )
    if blocked_text.search(code):
        return False, "high-risk primitive detected by heuristic lint"

    imports = re.findall(r"(?:^|\n)\s*(?:import\s+(\w+)|from\s+(\w+))", code)
    for module in [name for pair in imports for name in pair if name]:
        if module not in WHITELIST:
            return False, f"non-allowlisted import: {module}"
    return True, "heuristic lint passed; code remains untrusted"


def generate_tool(query):
    tokenizer, generator = _load_generator()
    messages = [
        {
            "role": "user",
            "content": (
                f"Write a Python script to: {query}.\n"
                "Define `def execute():` returning a string. "
                f"Use ONLY these modules: {', '.join(sorted(WHITELIST))}.\n"
                "Output only the code inside a ```python block."
            ),
        }
    ]
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    output = generator(prompt, max_new_tokens=300, do_sample=False)[0][
        "generated_text"
    ]
    match = re.search(r"```python\n(.*?)```", output, re.DOTALL)
    if not match:
        raise RuntimeError("model failed to generate a Python code block")
    return match.group(1)


def _restricted_import(name, globals=None, locals=None, fromlist=(), level=0):
    root = name.split(".", 1)[0]
    if root not in WHITELIST:
        raise ImportError(f"module is not allowlisted for unsafe research execution: {root}")
    return __import__(name, globals, locals, fromlist, level)


def _unsafe_execute_generated_code(code, *, allow_unsafe=False):
    """Legacy research execution. Deliberately difficult to enable; not a sandbox."""
    if not allow_unsafe:
        raise PermissionError("generated-code execution is disabled by default")
    if os.environ.get(UNSAFE_ACK_ENV) != UNSAFE_ACK_VALUE:
        raise PermissionError(
            f"set {UNSAFE_ACK_ENV}={UNSAFE_ACK_VALUE} to acknowledge unsafe execution"
        )

    research_builtins = {
        "__import__": _restricted_import,
        "abs": abs,
        "bool": bool,
        "dict": dict,
        "enumerate": enumerate,
        "Exception": Exception,
        "float": float,
        "int": int,
        "len": len,
        "list": list,
        "max": max,
        "min": min,
        "print": print,
        "range": range,
        "set": set,
        "str": str,
        "sum": sum,
        "tuple": tuple,
        "zip": zip,
    }
    globals_scope = {"__builtins__": research_builtins}
    local_scope = {}

    # This remains in-process execution of untrusted generated Python. The reduced
    # builtins/import surface is defense-in-depth only and MUST NOT be described as
    # a secure sandbox or used with secrets, privileged data, or trusted networks.
    exec(code, globals_scope, local_scope)
    entry = local_scope.get("execute", local_scope.get("execute_task"))
    if not callable(entry):
        raise RuntimeError("generated code did not define execute()")
    return str(entry())


def run(query, *, allow_unsafe=False, constellation=None):
    """Return a proposal by default; execute only after explicit unsafe opt-in."""
    constellation = _load_constellation() if constellation is None else constellation
    skill = find_skill(constellation, query)
    generated = skill is None

    if skill:
        code = str(skill.get("code", ""))
        description = str(skill.get("desc", "stored research skill"))
        print(f"[proposal] Reusing stored code for: {description}")
    else:
        print("[proposal] Generating tool code for review...")
        code = generate_tool(query)

    lint_ok, lint_message = lint_generated_code(code)
    if not lint_ok:
        return f"[blocked by heuristic lint] {lint_message}\n\n{code}"

    if not allow_unsafe:
        return (
            "[proposal only — NOT EXECUTED]\n"
            f"{lint_message}. Heuristic lint is not a sandbox.\n\n{code}"
        )

    result = _unsafe_execute_generated_code(code, allow_unsafe=True)
    if generated and result and "Error" not in result:
        save_skill(constellation, query, code)
    return result


def _parse_args():
    parser = argparse.ArgumentParser(
        description="ZWA Lite research artifact. Generated code is proposal-only by default."
    )
    parser.add_argument(
        "--unsafe-local-exec",
        action="store_true",
        help="enable legacy in-process generated-code execution; NOT a sandbox",
    )
    return parser.parse_args()


def main():
    args = _parse_args()
    if args.unsafe_local_exec:
        print("WARNING: unsafe local execution requested. This is NOT a sandbox.")
        if os.environ.get(UNSAFE_ACK_ENV) != UNSAFE_ACK_VALUE:
            raise SystemExit(
                f"Refusing execution. Set {UNSAFE_ACK_ENV}={UNSAFE_ACK_VALUE} only in an isolated research environment."
            )
    else:
        print("ZWA Lite proposal-only mode. Generated code will NOT execute.")

    while True:
        try:
            query = input("\nZ-Core> ")
        except (EOFError, KeyboardInterrupt):
            break
        if query.lower() in {"exit", "quit"}:
            break
        if not query.strip():
            continue
        try:
            print(run(query, allow_unsafe=args.unsafe_local_exec))
        except Exception as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()
