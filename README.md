# ZWA Lite – Zero-Weight Architecture v2.1 (Musk Build)

A single-file, self-expanding AI kernel. It builds Python micro-tools on demand, stores them in JSON, and reuses them forever.

## Quick Start
1. **Install:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run:**
   ```bash
   python zwa_lite.py
   ```
   (First run will auto-bootstrap 3 basic tools. ~2GB download for model.)

## Philosophy
"The best part is no part."

- **No Training:** Uses Phi-3-mini (3.8B) zero-shot.
- **No Database:** Stores skills in constellation.json.
- **No UI:** Pure CLI loop.
- **No Bloat:** <100 Lines of Code.

## Usage
Just ask for what you need. If the tool doesn't exist, Z-Core builds it.

```
Z-Core> fetch google.com and return the status code
Z-Core> calculate the square root of 529
```

## Performance Note
Uses 4-bit quantization by default (via bitsandbytes) to fit on consumer GPUs/CPUs.

For maximum speed on Apple Silicon (M1/M2/M3) or non-NVIDIA hardware, consider running the logic via llama.cpp or ollama.

Built by @zoverions (Zov), 2026. MIT License.
