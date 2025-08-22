# llm_review.py
'''
import argparse
import json
import os
import requests
import csv
from typing import Dict, Any, Optional, List, Tuple

def load_file(path, is_json=True):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f) if is_json else f.read().strip()
        except json.JSONDecodeError:
            return f.read().strip()

def build_prompt(doc_base, output_dir="outputs"):
    ocr_path = os.path.join(output_dir, f"{doc_base}_ocr.json")
    header_path = os.path.join(output_dir, f"{doc_base}_header.json")
    table_path = os.path.join(output_dir, f"{doc_base}_table_0.csv")
    warnings_path = os.path.join(output_dir, f"{doc_base}_warnings.json")

    ocr = load_file(ocr_path)
    header = load_file(header_path)
    table = load_file(table_path, is_json=False)
    warnings = load_file(warnings_path)

    sections = []
    if header:
        if isinstance(header, dict):
            sections.append("Header Info:\n" + "\n".join(f"{k}: {v}" for k, v in header.items()))
        else:
            sections.append("Header Info:\n" + str(header))

    if ocr:
        if isinstance(ocr, dict):
            ocr_text = json.dumps(ocr, indent=2, ensure_ascii=False)
        else:
            ocr_text = str(ocr)
        sections.append("Full OCR Text:\n" + ocr_text)

    if table:
        sections.append("Extracted Table:\n" + table)
    if warnings:
        if isinstance(warnings, list):
            joined = "\n".join(f"- {w}" for w in warnings)
        elif isinstance(warnings, dict) and "warnings" in warnings:
            joined = "\n".join(f"- {w}" for w in warnings["warnings"])
        else:
            joined = str(warnings)
        sections.append("Warnings:\n" + joined)
    else:
        sections.append("Warnings: None")
      
    instruction = """
        You are an expert civil engineering document reviewer.

        Write a detailed human-readable summary in the following sections:
        - Header Review
        - Document Purpose
        - Validation Warnings
        - Table Structure
        - Specific Content Issues
        - Final Evaluation

        Use bullet points. Do not use JSON. Be precise and helpful for construction engineers.
        """



    return "\n\n".join(sections + [instruction])

def _find_latest_base(outputs_dir: str) -> Optional[str]:
    """Pick most recent *_header.json and return its base name."""
    candidates: List[Tuple[str, float]] = []
    for f in os.listdir(outputs_dir):
        if f.endswith("_header.json"):
            path = os.path.join(outputs_dir, f)
            candidates.append((path, os.path.getmtime(path)))
    if not candidates:
        return None
    latest_header_path, _ = max(candidates, key=lambda x: x[1])
    return os.path.basename(latest_header_path)[:-len("_header.json")]

def _paths_for_base(outputs_dir: str, base: str) -> Dict[str, Optional[str]]:
    def p(name): return os.path.join(outputs_dir, name)
    def ensure(path): return path if path and os.path.exists(path) else None

    header_json = ensure(p(f"{base}_header.json"))
    # prefer *_full_text.json, fallback to *_ocr.json
    full_text_json = None
    for cand in (f"{base}_full_text.json", f"{base}_ocr.json"):
        cand_path = p(cand)
        if os.path.exists(cand_path):
            full_text_json = cand_path
            break

    warnings_json = None
    for cand in (f"{base}_warnings.json", f"{base}_warn.json"):
        cand_path = p(cand)
        if os.path.exists(cand_path):
            warnings_json = cand_path
            break

    table_csv = ensure(p(f"{base}_table_0.csv"))

    return {
        "header_json": header_json,
        "full_text_json": full_text_json,
        "warnings_json": warnings_json,
        "table_csv": table_csv,
    }

def _load_csv_rows(path: Optional[str]) -> List[Dict[str, str]]:
    if not path or not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]
  


def run_llm(prompt: str,
            base_url: str = "http://localhost:1234",
            model_name: Optional[str] = None,
            temperature: float = 0.2,
            max_tokens: int = 800) -> Dict[str, Any]:
    """Call a local OpenAI-compatible LLM server using streaming response."""
    
    url = f"{base_url.rstrip('/')}/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    model = model_name or os.getenv("LLM_MODEL") or "mistral"

    # Compose prompt as a single user message (no system role, Mistral-compatible)
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": (
                    "You are a professional civil engineering document reviewer. "
                    "Read the following extracted content and write a detailed summary including:\n"
                    "- Header fields review (missing/incomplete)\n"
                    "- Document purpose\n"
                    "- Warnings or data issues\n"
                    "- Table structure\n"
                    "- Row-level or cell-level problems\n"
                    "- Final assessment of completeness and consistency\n\n"
                    "Write in human-readable format using bullet points and section titles. "
                    "DO NOT use JSON format."
                    f"\n\n{prompt}"
                )
            }
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True
    }

    full_text = ""

    try:
        with requests.post(url, headers=headers, json=payload, stream=True, timeout=(10, 600)) as r:
            r.raise_for_status()
            for line in r.iter_lines(decode_unicode=True):
                if line and line.startswith("data: "):
                    chunk = line[len("data: "):]
                    if chunk == "[DONE]":
                        break
                    try:
                        data = json.loads(chunk)
                        delta = data["choices"][0]["delta"].get("content", "")
                        full_text += delta
                    except Exception:
                        continue

    except requests.exceptions.RequestException as e:
        return {"error": f"LLM request failed: {e}"}

    return {"model": model, "output": full_text.strip()}




def run_review(outputs_dir: str = "outputs",
               base: Optional[str] = None,
               llm_base_url: str = "http://localhost:1234",
               model: Optional[str] = None,
               temperature: float = 0.2) -> Dict[str, Any]:
    """
    Loads header/ocr/table from outputs/, sends to LLM, saves structured .txt summary, and returns output.
    """
    if not base:
        base = _find_latest_base(outputs_dir)
        if not base:
            return {"error": "No processed bundle found in /outputs."}

    prompt = build_prompt(base, output_dir=outputs_dir)
    try:
        llm_res = run_llm(prompt, base_url=llm_base_url, model_name=model, temperature=temperature)
    except requests.RequestException as e:
        return {"error": f"LLM request failed: {e}", "base": base}

    # 📝 Write structured .txt summary
    review_text = llm_res["output"]
    txt_path = os.path.join(outputs_dir, f"{base}_llm_review.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(review_text.strip())

    # 📦 Return metadata
    paths = _paths_for_base(outputs_dir, base)
    return {
        "base": base,
        "files_used": paths,
        "model": llm_res["model"],
        "review_txt": f"/outputs/{os.path.basename(txt_path)}",
        "output": review_text.strip()
    }


# (Optional) keep the CLI for ad-hoc usage
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--doc", required=True, help="Document basename without suffixes")
    args = parser.parse_args()

    prompt = build_prompt(args.doc)
    print("📨 Prompt ready. Sending to LLM...\n")
    res = run_llm(prompt)
    print("\n===== 🤖 LLM DOCUMENT REVIEW =====\n")
    print(res["output"])

if __name__ == "__main__":
    main()


# Newwest script with max tokens 

# llm_review.py — robust LLM review with endpoint fallback + safe retries
import os, json, requests
from typing import Dict, Any, Optional, List, Tuple

# ---------------- Speed/robustness knobs (override via env) ----------------
MAX_FULLTEXT_CHARS = int(os.getenv("LLM_FULLTEXT_CHARS", "500"))   # tighter trim
MAX_CSV_LINES      = int(os.getenv("LLM_CSV_LINES", "8"))
MAX_TOKENS         = int(os.getenv("LLM_MAX_TOKENS", "180"))
REQUEST_TIMEOUT_S  = int(os.getenv("LLM_TIMEOUT_S", "300"))
CONNECT_TIMEOUT_S  = int(os.getenv("LLM_CONNECT_TIMEOUT_S", "10"))
FAST_MODE          = os.getenv("LLM_FAST", "0") == "1"
ENDPOINT_PREF      = os.getenv("LLM_ENDPOINT_PREF", "").strip().lower()  # "chat" | "completions" | ""
if FAST_MODE:
    MAX_FULLTEXT_CHARS = min(MAX_FULLTEXT_CHARS, 400)
    MAX_CSV_LINES = min(MAX_CSV_LINES, 6)
    MAX_TOKENS = min(MAX_TOKENS, 140)

# ---------------- File helpers ----------------
def _ensure_exists(path: Optional[str]) -> Optional[str]:
    return path if path and os.path.exists(path) else None

def _prefer_full_text(outputs_dir: str, base: str) -> Optional[str]:
    for name in (f"{base}_full_text.json", f"{base}_page1_full_text.json", f"{base}_ocr.json"):
        p = os.path.join(outputs_dir, name)
        if os.path.exists(p): return p
    return None

def _paths_for_base(outputs_dir: str, base: str) -> Dict[str, Optional[str]]:
    def p(name): return os.path.join(outputs_dir, name)
    return {
        "header_json":   _ensure_exists(p(f"{base}_header.json")),
        "full_text_json":_ensure_exists(_prefer_full_text(outputs_dir, base)),
        "warnings_json": _ensure_exists(p(f"{base}_warnings.json")) or _ensure_exists(p(f"{base}_warn.json")),
        "table_csv":     _ensure_exists(p(f"{base}_table_0.csv")) or _ensure_exists(p(f"{base}_page1_table_0.csv")),
        "review_txt":    _ensure_exists(p(f"{base}_llm_review.txt")),
    }

def _load_file(path: str, is_json=True):
    with open(path, "r", encoding="utf-8") as f:
        if is_json:
            try:    return json.load(f)
            except: return f.read().strip()
        return f.read().strip()

def _load_csv_excerpt(path: Optional[str], max_lines: int) -> str:
    if not path or not os.path.exists(path): return ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return "".join(f.readlines()[:max_lines])
    except:
        return ""

def _mtime(path: Optional[str]) -> float:
    try: return os.path.getmtime(path) if path else 0.0
    except: return 0.0

def _find_latest_base(outputs_dir: str) -> Optional[str]:
    cand: List[Tuple[str, float]] = []
    for f in os.listdir(outputs_dir):
        if f.endswith("_header.json"):
            p = os.path.join(outputs_dir, f)
            cand.append((p, os.path.getmtime(p)))
    if not cand: return None
    latest, _ = max(cand, key=lambda x: x[1])
    return os.path.basename(latest)[:-len("_header.json")]

def _needs_refresh(paths: Dict[str, Optional[str]]) -> bool:
    rev_m = _mtime(paths.get("review_txt"))
    if rev_m == 0: return True
    for k in ("header_json", "full_text_json", "warnings_json", "table_csv"):
        if _mtime(paths.get(k)) > rev_m: return True
    return False

# ---------------- Prompt builder (compact & human) ----------------
def build_prompt(base: str, outputs_dir: str = "outputs") -> str:
    paths = _paths_for_base(outputs_dir, base)
    sections: List[str] = []

    # Header (compact)
    if paths["header_json"]:
        hdr = _load_file(paths["header_json"], is_json=True)
        if isinstance(hdr, dict):
            items = list(hdr.items())[:12]  # cap keys
            sections.append("Header Info:\n" + "\n".join(f"{k}: {v}" for k, v in items))
        else:
            sections.append("Header Info:\n" + str(hdr))

    # OCR text (truncate hard)
    if paths["full_text_json"]:
        ft = _load_file(paths["full_text_json"], is_json=True)
        ft_text = json.dumps(ft, ensure_ascii=False) if isinstance(ft, (dict, list)) else str(ft)
        if len(ft_text) > MAX_FULLTEXT_CHARS:
            ft_text = ft_text[:MAX_FULLTEXT_CHARS] + "\n[...truncated...]"
        sections.append("Full OCR Text (truncated):\n" + ft_text)

    # CSV excerpt
    if paths["table_csv"]:
        sections.append("Extracted Table (first rows):\n" + _load_csv_excerpt(paths["table_csv"], MAX_CSV_LINES))

    # Warnings (cap)
    if paths["warnings_json"]:
        w = _load_file(paths["warnings_json"], is_json=True)
        if isinstance(w, dict) and "warnings" in w:  items = w["warnings"]
        elif isinstance(w, list):                    items = w
        else:                                        items = [str(w)]
        items = items[:12]
        sections.append("Warnings (sample):\n" + "\n".join(f"- {itm}" for itm in items))
    else:
        sections.append("Warnings: None")

    instruction = (
        "You are a senior construction engineer and technical editor. Read the material and write a helpful, "
        "human-sounding review for a colleague who will attach it to a QA report.\n\n"
        "Write 2–3 short paragraphs followed by a few concise bullets covering:\n"
        "• Overall summary — what the document appears to be and whether it looks self-consistent.\n"
        "• Header assessment — which key fields were detected, which are missing/unclear, and any odd dates/IDs.\n"
        "• Table assessment — column semantics you infer, row grouping/totals, decimal style (comma vs dot), and any blank or misaligned cells.\n"
        "• Data quality checks — unit consistency (mm/m/kg), plausibility of Stück × Einzellänge ≈ Gesamtlänge, and obvious outliers.\n"
        "• Actionable next steps — concrete fixes or checks (e.g., re-OCR specific region, adjust header mapping, enable translated headers, re-run validation).\n\n"
        "Keep a professional but natural tone. Prefer plain language over jargon. If something is unknown, say so explicitly. "
        "Do not invent numbers that are not present in the inputs. End with a one-line ‘Verdict: …’ statement and finally the token <END> on its own line."
    )
    prompt = "\n\n".join(sections + [instruction])

    # absolute final safeguard: hard cap huge prompts
    if len(prompt) > 6000:
        prompt = prompt[:6000] + "\n[...truncated...]\n<END>"
    return prompt

# ---------------- LM Studio call with fallback & retry ----------------
def run_llm(prompt: str,
            base_url: str = "http://127.0.0.1:1234",
            model_name: Optional[str] = None,
            temperature: float = 0.2,
            max_tokens: int = MAX_TOKENS) -> Dict[str, Any]:
    """
    1) prefer chat/completions (unless LLM_ENDPOINT_PREF forces otherwise)
    2) fall back to /v1/completions
    3) retry once with smaller max_tokens and no stop (handles Channel Error/prediction-error)
    """
    base = base_url.rstrip("/")
    model = model_name or os.getenv("LLM_MODEL") or "mistral-7b-instruct-v0.3"

    def _chat_call(use_stop: bool = True) -> Dict[str, Any]:
        url = f"{base}/v1/chat/completions"
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        if use_stop:
            payload["stop"] = ["<END>"]
        r = requests.post(url, json=payload, timeout=(CONNECT_TIMEOUT_S, REQUEST_TIMEOUT_S))
        r.raise_for_status()
        data = r.json()
        text = data["choices"][0]["message"]["content"].strip()
        if use_stop and text.endswith("<END>"):
            text = text[:-5].rstrip()
        return {"model": model, "output": text, "endpoint": "chat"}

    def _comp_call(use_stop: bool = True, mt: int = max_tokens) -> Dict[str, Any]:
        url = f"{base}/v1/completions"
        payload = {
            "model": model,
            "prompt": (prompt + "\n<END>") if use_stop else prompt,
            "temperature": temperature,
            "max_tokens": mt,
            "stream": False
        }
        if use_stop:
            payload["stop"] = ["<END>"]
        r = requests.post(url, json=payload, timeout=(CONNECT_TIMEOUT_S, REQUEST_TIMEOUT_S))
        r.raise_for_status()
        data = r.json()
        text = (data["choices"][0].get("text") or "").strip()
        if use_stop and text.endswith("<END>"):
            text = text[:-5].rstrip()
        return {"model": model, "output": text, "endpoint": "completions"}

    # Order based on preference or default
    try_order = []
    if ENDPOINT_PREF == "chat":
        try_order = ["chat", "comp"]
    elif ENDPOINT_PREF == "completions":
        try_order = ["comp", "chat"]
    else:
        try_order = ["chat", "comp"]

    # Try primary
    try:
        if try_order[0] == "chat":
            return _chat_call(use_stop=True)
        else:
            return _comp_call(use_stop=True, mt=max_tokens)
    except requests.exceptions.RequestException:
        pass  # fall through

    # Try secondary
    try:
        if try_order[1] == "chat":
            return _chat_call(use_stop=True)
        else:
            return _comp_call(use_stop=True, mt=max_tokens)
    except requests.exceptions.RequestException:
        pass  # fall through

    # Final retry: completions, no stop, smaller budget (handles Channel Error / 400)
    try:
        return _comp_call(use_stop=False, mt=max(80, min(140, max_tokens // 2)))
    except requests.exceptions.RequestException as e3:
        return {"error": f"LLM failed on all attempts: {e3}"}

# ---------------- Public API ----------------
def run_review(outputs_dir: str = "outputs",
               base: Optional[str] = None,
               llm_base_url: str = "http://127.0.0.1:1234",
               model: Optional[str] = None,
               temperature: float = 0.2,
               force: bool = False) -> Dict[str, Any]:
    if not base:
        base = _find_latest_base(outputs_dir)
        if not base:
            return {"error": "No processed bundle found in /outputs."}

    paths = _paths_for_base(outputs_dir, base)

    if not force and not _needs_refresh(paths) and paths["review_txt"]:
        return {
            "base": base,
            "model": model or os.getenv("LLM_MODEL") or "mistral-7b-instruct-v0.3",
            "endpoint": None,
            "review_txt": f"/outputs/{os.path.basename(paths['review_txt'])}",
            "output": _load_file(paths["review_txt"], is_json=False)
        }

    prompt = build_prompt(base, outputs_dir=outputs_dir)
    res = run_llm(prompt, base_url=llm_base_url, model_name=model, temperature=temperature)
    review_text = res.get("output") or f"(LLM review unavailable: {res.get('error')})"

    out_path = os.path.join(outputs_dir, f"{base}_llm_review.txt")
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(review_text.strip())
    except Exception:
        pass

    return {
        "base": base,
        "files_used": paths,
        "model": res.get("model") or model or "mistral-7b-instruct-v0.3",
        "endpoint": res.get("endpoint"),
        "review_txt": f"/outputs/{os.path.basename(out_path)}",
        "output": review_text.strip()
    }
'''
 
# llm_review.py — robust LM Studio review with defaults, health-check, fallback, and junk-output guard

import os, json, requests
from typing import Dict, Any, Optional, List, Tuple

# ------------------------------------------------------------------
# Built-in defaults (overridable via OS env)
# ------------------------------------------------------------------
_DEFAULTS = {
    "LLM_BASE_URL":            "http://127.0.0.1:1234",
    "LLM_MODEL":               "mistral-7b-instruct-v0.3",
    "LLM_ENDPOINT_PREF":       "chat",   # "chat" or "completions" (chat is more stable in LM Studio)
    "LLM_FULLTEXT_CHARS":      "1400",   # OCR text included in prompt
    "LLM_CSV_LINES":           "12",     # table lines included in prompt
    "LLM_MAX_TOKENS":          "220",    # 0 => unlimited (we rely on <END>)
    "LLM_TIMEOUT_S":           "75",
    "LLM_CONNECT_TIMEOUT_S":   "10",
    "LLM_FAST":                "1",
    "LLM_TEMPERATURE":         "0.2",
}

def _env(k: str, fallback: Optional[str] = None) -> str:
    return os.getenv(k, _DEFAULTS.get(k, fallback) if fallback is None else fallback)

# Effective limits (with FAST mode trimming)
MAX_FULLTEXT_CHARS = int(_env("LLM_FULLTEXT_CHARS"))
MAX_CSV_LINES      = int(_env("LLM_CSV_LINES"))
FAST_MODE          = _env("LLM_FAST") == "1"
if FAST_MODE:
    MAX_FULLTEXT_CHARS = min(MAX_FULLTEXT_CHARS, 1000)
    MAX_CSV_LINES      = min(MAX_CSV_LINES, 10)

CONNECT_TIMEOUT_S  = int(_env("LLM_CONNECT_TIMEOUT_S"))
REQUEST_TIMEOUT_S  = int(_env("LLM_TIMEOUT_S"))
ENDPOINT_PREF      = (_env("LLM_ENDPOINT_PREF") or "chat").strip().lower()  # "chat" | "completions"

# ---------------- File helpers ----------------
def _ensure_exists(path: Optional[str]) -> Optional[str]:
    return path if path and os.path.exists(path) else None

def _prefer_full_text(outputs_dir: str, base: str) -> Optional[str]:
    for name in (f"{base}_full_text.json", f"{base}_page1_full_text.json", f"{base}_ocr.json"):
        p = os.path.join(outputs_dir, name)
        if os.path.exists(p):
            return p
    return None

def _paths_for_base(outputs_dir: str, base: str) -> Dict[str, Optional[str]]:
    def p(name): return os.path.join(outputs_dir, name)
    return {
        "header_json":    _ensure_exists(p(f"{base}_header.json")),
        "full_text_json": _ensure_exists(_prefer_full_text(outputs_dir, base)),
        "warnings_json":  _ensure_exists(p(f"{base}_warnings.json")) or _ensure_exists(p(f"{base}_warn.json")),
        "table_csv":      _ensure_exists(p(f"{base}_table_0.csv")) or _ensure_exists(p(f"{base}_page1_table_0.csv")),
        "review_txt":     _ensure_exists(p(f"{base}_llm_review.txt")),
    }

def _load_file(path: str, is_json=True):
    with open(path, "r", encoding="utf-8") as f:
        if is_json:
            try:    return json.load(f)
            except: return f.read().strip()
        return f.read().strip()

def _load_csv_excerpt(path: Optional[str], max_lines: int) -> str:
    if not path or not os.path.exists(path): return ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return "".join(f.readlines()[:max_lines])
    except:
        return ""

def _mtime(path: Optional[str]) -> float:
    try: return os.path.getmtime(path) if path else 0.0
    except: return 0.0

def _find_latest_base(outputs_dir: str) -> Optional[str]:
    cand: List[Tuple[str, float]] = []
    for f in os.listdir(outputs_dir):
        if f.endswith("_header.json"):
            p = os.path.join(outputs_dir, f)
            cand.append((p, os.path.getmtime(p)))
    if not cand: return None
    latest, _ = max(cand, key=lambda x: x[1])
    return os.path.basename(latest)[:-len("_header.json")]

def _needs_refresh(paths: Dict[str, Optional[str]]) -> bool:
    rev_m = _mtime(paths.get("review_txt"))
    if rev_m == 0:  # no review yet
        return True
    for k in ("header_json", "full_text_json", "warnings_json", "table_csv"):
        if _mtime(paths.get(k)) > rev_m: return True
    return False

# ---------------- Prompt builder (cleaner header + human style) ----------------
def _fmt_header_value(v):
    s = str(v or "").strip()
    if not s:
        return ""
    # require ~40% alnum → drop noisy OCR gibberish
    if sum(ch.isalnum() for ch in s) < max(4, int(0.4 * len(s))):
        return ""
    return " ".join(s.split())

def _select_header_fields(hdr: dict):
    prefer = ["PROJECT", "DRAWING_NO", "DATE", "PERSON", "AUTHOR", "Hinweis", "Plan", "Objekt"]
    out = []
    for k in prefer:
        if k in hdr:
            val = _fmt_header_value(hdr.get(k))
            if val:
                out.append((k, val))
    for k, v in hdr.items():
        if k in dict(out) or k.lower().startswith("raw_") or k.lower() == "raw_ocr_text":
            continue
        val = _fmt_header_value(v)
        if val and len(val) <= 120:
            out.append((k, val))
        if len(out) >= 10:
            break
    return out

def build_prompt(base: str, outputs_dir: str = "outputs") -> str:
    paths = _paths_for_base(outputs_dir, base)
    sections: List[str] = []

    # Header (clean)
    if paths["header_json"]:
        hdr = _load_file(paths["header_json"], is_json=True)
        if isinstance(hdr, dict):
            items = _select_header_fields(hdr)
            if items:
                sections.append("Header Info:\n" + "\n".join(f"{k}: {v}" for k, v in items))
            else:
                sections.append("Header Info: (fields unreadable or missing)")
        else:
            sections.append("Header Info: (unstructured)")

    # Full OCR text (truncate)
    if paths["full_text_json"]:
        ft = _load_file(paths["full_text_json"], is_json=True)
        ft_text = json.dumps(ft, ensure_ascii=False) if isinstance(ft, (dict, list)) else str(ft)
        if len(ft_text) > MAX_FULLTEXT_CHARS:
            ft_text = ft_text[:MAX_FULLTEXT_CHARS] + "\n[...truncated...]"
        sections.append("Full OCR Text (truncated):\n" + ft_text)

    # CSV excerpt
    if paths["table_csv"]:
        sections.append("Extracted Table (first rows):\n" + _load_csv_excerpt(paths["table_csv"], MAX_CSV_LINES))

    # Warnings
    if paths["warnings_json"]:
        w = _load_file(paths["warnings_json"], is_json=True)
        items = w.get("warnings", w) if isinstance(w, dict) else (w if isinstance(w, list) else [str(w)])
        sections.append("Warnings (sample):\n" + "\n".join(f"- {itm}" for itm in items[:12]))
    else:
        sections.append("Warnings: None")

    instruction = (
        "You are a senior construction engineer and technical editor. Read the material and write a helpful, "
        "human-sounding review for a colleague who will attach it to a QA report.\n\n"
        "Write 2–3 short paragraphs followed by a few concise bullets covering:\n"
        "• Overall summary — what the document appears to be and whether it looks self-consistent.\n"
        "• Header assessment — which key fields were detected, which are missing/unclear, and any odd dates/IDs.\n"
        "• Table assessment — column semantics you infer, row grouping/totals, decimal style (comma vs dot), and any blank or misaligned cells.\n"
        "• Data quality checks — unit consistency (mm/m/kg), plausibility of Stück × Einzellänge ≈ Gesamtlänge, and obvious outliers.\n"
        "• Actionable next steps — concrete fixes or checks (e.g., re-OCR specific region, adjust header mapping, enable translated headers, re-run validation).\n\n"
        "Keep a professional but natural tone. Prefer plain language over jargon. If something is unknown, say so explicitly. "
        "Do not invent numbers that are not present in the inputs. End with a one-line ‘Verdict: …’ statement and finally the token <END> on its own line."
    )
    prompt = "\n\n".join(sections + [instruction])

    # Hard cap giant prompts to avoid engine instability
    if len(prompt) > 6000:
        prompt = prompt[:6000] + "\n[...truncated...]\n<END>"
    return prompt

# ---------------- Junk-output detector ----------------
def _looks_garbage(text: str) -> bool:
    t = text.strip()
    if len(t) < 60:
        return True
    if t.lower().startswith("ok, i"):
        return True
    # many repeated characters (like x x x ...)
    uniq = set(t.replace("\n", "").replace(" ", ""))
    if len(uniq) <= max(3, int(0.15 * len(set(t)))):
        return True
    # lines that are almost the same character
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
    if lines and sum(1 for ln in lines if len(set(ln)) <= 2) / len(lines) > 0.5:
        return True
    return False

# ---------------- LM Studio call with health-check, fallback & rescue ----------------
def run_llm(prompt: str,
            base_url: Optional[str] = None,
            model_name: Optional[str] = None,
            temperature: Optional[float] = None,
            max_tokens: Optional[int] = None) -> Dict[str, Any]:

    base = (base_url or _env("LLM_BASE_URL")).rstrip("/")
    model = model_name or _env("LLM_MODEL")
    temp  = float(_env("LLM_TEMPERATURE", str(temperature if temperature is not None else 0.2)))

    # Token policy: 0 => "unlimited" (omit max_tokens; rely on <END>)
    raw = _env("LLM_MAX_TOKENS", str(max_tokens if max_tokens is not None else ""))
    try:
        raw_i = int(raw) if raw != "" else None
    except:
        raw_i = None

    def _effective_max_tokens():
        if raw_i is None:
            return None
        return None if raw_i <= 0 else raw_i

    # Health check
    try:
        r0 = requests.get(f"{base}/v1/models", timeout=(CONNECT_TIMEOUT_S, 15))
        r0.raise_for_status()
        ids = [m.get("id") for m in r0.json().get("data", [])]
        if model not in ids:
            return {"error": f"Model '{model}' not in /v1/models list.", "endpoint": "models"}
    except requests.exceptions.RequestException as e:
        return {"error": f"LLM server not ready: {e}", "endpoint": "models"}

    stops = ["<END>"]

    def _chat_call(use_stop: bool = True, mt: Optional[int] = _effective_max_tokens()) -> Dict[str, Any]:
        url = f"{base}/v1/chat/completions"
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temp,
            "stream": False
        }
        if use_stop: payload["stop"] = stops
        if mt is not None and mt > 0: payload["max_tokens"] = mt
        r = requests.post(url, json=payload, timeout=(CONNECT_TIMEOUT_S, REQUEST_TIMEOUT_S))
        r.raise_for_status()
        data = r.json()
        text = data["choices"][0]["message"]["content"].strip()
        if use_stop and text.endswith("<END>"): text = text[:-5].rstrip()
        return {"model": model, "output": text, "endpoint": "chat"}

    def _comp_call(use_stop: bool = True, mt: Optional[int] = _effective_max_tokens()) -> Dict[str, Any]:
        url = f"{base}/v1/completions"
        payload = {
            "model": model,
            "prompt": prompt + ("\n<END>" if use_stop else ""),
            "temperature": temp,
            "stream": False
        }
        if use_stop: payload["stop"] = stops
        if mt is not None and mt > 0: payload["max_tokens"] = mt
        r = requests.post(url, json=payload, timeout=(CONNECT_TIMEOUT_S, REQUEST_TIMEOUT_S))
        r.raise_for_status()
        data = r.json()
        text = (data["choices"][0].get("text") or "").strip()
        if use_stop and text.endswith("<END>"): text = text[:-5].rstrip()
        return {"model": model, "output": text, "endpoint": "completions"}

    order = ["chat", "comp"] if ENDPOINT_PREF != "completions" else ["comp", "chat"]

    # Primary
    try:
        res = _chat_call(True) if order[0] == "chat" else _comp_call(True)
        if not _looks_garbage(res["output"]):
            return res
    except requests.exceptions.RequestException:
        res = None

    # Secondary
    try:
        res2 = _chat_call(True) if order[1] == "chat" else _comp_call(True)
        if not _looks_garbage(res2["output"]):
            return res2
    except requests.exceptions.RequestException:
        res2 = None

    # Final rescue: small cap, no stop (works around “Channel Error”/“prediction-error”)
    try:
        retry_cap = 160
        res3 = _comp_call(use_stop=False, mt=retry_cap)
        return res3
    except requests.exceptions.RequestException as e3:
        return {"error": f"LLM failed on all attempts: {e3}"}

# ---------------- Public API ----------------
def run_review(outputs_dir: str = "outputs",
               base: Optional[str] = None,
               llm_base_url: Optional[str] = None,
               model: Optional[str] = None,
               temperature: float = 0.2,
               force: bool = False) -> Dict[str, Any]:

    if not base:
        base = _find_latest_base(outputs_dir)
        if not base:
            return {"error": "No processed bundle found in /outputs."}

    paths = _paths_for_base(outputs_dir, base)

    # Cached?
    if not force and not _needs_refresh(paths) and paths.get("review_txt"):
        return {
            "base": base,
            "model": model or _env("LLM_MODEL"),
            "endpoint": None,
            "review_txt": f"/outputs/{os.path.basename(paths['review_txt'])}",
            "output": _load_file(paths["review_txt"], is_json=False),
        }

    prompt = build_prompt(base, outputs_dir=outputs_dir)
    print("LLM: payload stats →", {
        "prompt_chars": len(prompt),
        "full_text_limit": MAX_FULLTEXT_CHARS,
        "csv_lines": MAX_CSV_LINES,
        "fast": FAST_MODE,
        "endpoint_pref": ENDPOINT_PREF,
    })

    res = run_llm(
        prompt,
        base_url=llm_base_url or _env("LLM_BASE_URL"),
        model_name=model or _env("LLM_MODEL"),
        temperature=temperature,
        max_tokens=None,  # we manage tokens inside run_llm via env
    )
    review_text = res.get("output") or f"(LLM review unavailable: {res.get('error')})"

    out_path = os.path.join(outputs_dir, f"{base}_llm_review.txt")
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(review_text.strip())
    except Exception:
        pass

    return {
        "base": base,
        "files_used": paths,
        "model": res.get("model") or model or _env("LLM_MODEL"),
        "endpoint": res.get("endpoint"),
        "review_txt": f"/outputs/{os.path.basename(out_path)}",
        "output": review_text.strip(),
    }
