'''
 # 2nd Old Script  
# app.py — FastAPI backend for OCR table extraction, LLM review & PDF

from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import os
import shutil
import uuid
import zipfile
import traceback
from pathlib import Path
import pprint

from core.extractor import SmartTableExtractor
from core.config import load_config
from pdf_report import generate_pdf_report
from llm_review import run_review


# ----------------------------
# Setup
# ----------------------------

# Ensure folders exist BEFORE mounting static files
os.makedirs("outputs", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static mounts
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Config & extractor
cfg = load_config("configs/default.yaml")
yolo_weights = (cfg.get("model", {}) or {}).get("yolo_weights") or "pixocr_modules/model/best.pt"

extractor = SmartTableExtractor(
    yolo_model_path=yolo_weights,
    output_dir="outputs",
    config=cfg,
    translate_headers=False,   # can be overridden per request
    validate_schema=False,
    debug=True                 # keep True so *_full_text.json is persisted
)


# ----------------------------
# Helpers
# ----------------------------

def _llm_base_url() -> str:
    return os.getenv("LLM_BASE_URL", "http://localhost:1234")

def _to_url(path: str | None) -> str | None:
    """Convert a filesystem path under outputs/ to a /outputs/ URL if it exists."""
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        # accept already-URL-looking inputs like "/outputs/foo.png" and rewrite if file exists
        if str(path).startswith("/outputs/"):
            p = Path("outputs") / Path(path).name
            if not p.exists():
                return None
        else:
            return None
    return f"/outputs/{p.name}"

def _as_fs(path_or_url: str | None) -> str | None:
    """Ensure we hand a real filesystem path to the PDF generator."""
    if not path_or_url:
        return None
    s = str(path_or_url)
    if s.startswith("/outputs/"):
        return str(Path("outputs") / Path(s).name)
    return s

def _detect_review_base(base_name: str) -> str | None:
    """
    Pick the correct 'base' for run_review(), depending on filenames in outputs/.
    Prefer <base>, fall back to <base>_page1, otherwise try any <base>*_header.json first match.
    """
    candidates = [
        base_name,
        f"{base_name}_page1",
    ]
    for b in candidates:
        if Path(f"outputs/{b}_header.json").exists():
            return b
    # last resort: find any file that starts with base and ends with _header.json
    for p in Path("outputs").glob(f"{base_name}*_header.json"):
        return p.name[:-len("_header.json")]
    return None

def _attach_llm_review_to_result(result: dict, review_base: str) -> None:
    """Attach LLM review file path & text to result for the PDF."""
    review_path = Path("outputs") / f"{review_base}_llm_review.txt"
    if review_path.exists():
        result["llm_review_txt_path"] = str(review_path)
        try:
            with open(review_path, "r", encoding="utf-8") as f:
                result["llm_review_text"] = f.read()
        except Exception:
            pass

def _prepare_result_for_pdf(result: dict) -> dict:
    """
    Return a shallow copy of result where all paths are filesystem paths.
    This is what generate_pdf_report expects.
    """
    r = dict(result)
    # Normalize common fields (fs paths)
    for k in ("original_image", "header_json", "full_text_json", "table_crop_image", "llm_review_txt_path"):
        if r.get(k):
            r[k] = _as_fs(r[k])
    # Table CSV list
    if r.get("table_csvs"):
        r["table_csvs"] = [_as_fs(p) for p in r["table_csvs"] if p]
    # Tables array (images inside)
    if r.get("tables"):
        r["tables"] = [
            {**t, "image": _as_fs(t.get("image")) if t.get("image") else None}
            for t in r["tables"]
        ]
    return r


# ----------------------------
# API
# ----------------------------

@app.post("/process")
async def process_document(
    file: UploadFile = File(...),
    translate_headers: bool = Query(False, description="Map headers to canonical names (validator-friendly)"),
    generate_pdf: bool = Query(True, description="Generate PDF report after extraction & review"),
):
    """
    Upload an image/PDF page, run YOLO+OCR extraction, run LLM review, then build the PDF.
    Response returns web-friendly URLs for the frontend.
    """
    try:
        # 1) Save upload
        input_filename = f"uploads/{uuid.uuid4().hex}_{file.filename}"
        with open(input_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2) Extract (use per-request translate flag)
        extractor.translate_headers = bool(translate_headers)
        result = extractor.process(input_filename)

        # Base name (of the uploaded file)
        base_name = os.path.splitext(os.path.basename(input_filename))[0]

        # 3) Copy original upload to outputs (so it's visible in UI)
        output_original_path = os.path.join("outputs", os.path.basename(input_filename))
        shutil.copy(input_filename, output_original_path)

        # Prefer extractor's page PNG for the PDF "original_image"; else fall back to copied upload
        # (extractor already saved <base>.png in outputs and set result["original_image"] to /outputs/..)
        if not result.get("original_image"):
            result["original_image"] = output_original_path  # filesystem path for now

        # 4) LLM review BEFORE PDF
        # Pick the correct base for review files (handles <base> or <base>_page1 variants)
        review_base = _detect_review_base(base_name) or base_name
        _ = run_review(
            outputs_dir="outputs",
            base=review_base,
            llm_base_url=_llm_base_url(),
            model="mistral",
            temperature=0.2,
        )
        _attach_llm_review_to_result(result, review_base)

        # 5) Generate PDF (hand real filesystem paths)
        if generate_pdf:
            pdf_path = os.path.join("outputs", f"{base_name}_report.pdf")
            result_for_pdf = _prepare_result_for_pdf(result)
            generate_pdf_report(result_for_pdf, pdf_path)
            result["report_pdf"] = pdf_path  # keep fs path for now

        # 6) Convert to URLs for frontend
        result["original_image"]   = _to_url(result.get("original_image") or output_original_path)
        result["header_json"]      = _to_url(result.get("header_json"))
        result["full_text_json"]   = _to_url(result.get("full_text_json"))
        result["table_crop_image"] = _to_url(result.get("table_crop_image"))
        result["table_csvs"]       = [_to_url(p) for p in result.get("table_csvs", []) if p]

        # LLM review URL
        if result.get("llm_review_txt_path"):
            result["llm_review_txt"] = _to_url(result["llm_review_txt_path"])

        # PDF URL
        if result.get("report_pdf"):
            result["report_pdf"] = _to_url(result["report_pdf"])

        pprint.pprint(result)
        return JSONResponse(content=result)

    except Exception as e:
        print("❌ Extraction failed:")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/review")
def review_endpoint(
    base: str = Query(..., description="Base name without suffix (e.g., '<upload>' or '<upload>_page1')."),
    model: str = Query("mistral", description="Model ID on your local server."),
    temperature: float = Query(0.2, ge=0.0, le=1.0),
):
    """
    Re-run review on an already processed bundle in /outputs.
    """
    result = run_review(
        outputs_dir="outputs",
        base=base,
        llm_base_url=_llm_base_url(),
        model=model,
        temperature=temperature,
    )
    status = 200 if "error" not in result else 500
    return JSONResponse(content=result, status_code=status)


@app.get("/zip")
def download_zip():
    zip_path = "outputs/results.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for root, _, files in os.walk("outputs"):
            for file in files:
                if file.endswith((".csv", ".json", ".png", ".txt", ".pdf")):
                    zipf.write(os.path.join(root, file), arcname=file)
    return FileResponse(zip_path, filename="processed_results.zip")

 
'''
# app.py — FastAPI backend for OCR table extraction, LLM review, validation & PDF (with stage logs)
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import os, shutil, uuid, zipfile, traceback, time, json, requests
from pathlib import Path
import pprint

from core.extractor import SmartTableExtractor
from core.config import load_config
from pdf_report import generate_pdf_report
from llm_review import run_review as do_run_review

# ──────────────────────────────────────────────────────────────────────────────
# Setup
# ──────────────────────────────────────────────────────────────────────────────
os.makedirs("outputs", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

cfg = load_config("configs/default.yaml")
yolo_weights = (cfg.get("model", {}) or {}).get("yolo_weights") or "pixocr_modules/model/best.pt"

extractor = SmartTableExtractor(
    yolo_model_path=yolo_weights,
    output_dir="outputs",
    config=cfg,
    translate_headers=False,   # override per request
    validate_schema=True,      # default on
    debug=True                 # keep *_full_text.json for PDF/LLM
)

# ──────────────────────────────────────────────────────────────────────────────
# Env defaults (so it "just works" on localhost)
# ──────────────────────────────────────────────────────────────────────────────
os.environ.setdefault("LLM_BASE_URL", "http://127.0.0.1:1234")
os.environ.setdefault("LLM_MODEL", "mistral-7b-instruct-v0.3")
os.environ.setdefault("LLM_ENDPOINT_PREF", "completions")

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def _llm_base_url() -> str:
    return os.getenv("LLM_BASE_URL", "http://127.0.0.1:1234")

def _to_url(path: str | None) -> str | None:
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        if str(path).startswith("/outputs/"):
            p = Path("outputs") / Path(path).name
            if not p.exists():
                return None
        else:
            return None
    return f"/outputs/{p.name}"

def _as_fs(path_or_url: str | None) -> str | None:
    if not path_or_url:
        return None
    s = str(path_or_url)
    if s.startswith("/outputs/"):
        return str(Path("outputs") / Path(s).name)
    return s

def _detect_review_base(base_name: str) -> str | None:
    for b in (base_name, f"{base_name}_page1"):
        if Path(f"outputs/{b}_header.json").exists():
            return b
    for p in Path("outputs").glob(f"{base_name}*_header.json"):
        return p.name[:-len("_header.json")]
    return None

def _attach_llm_review_to_result(result: dict, review_base: str) -> None:
    review_path = Path("outputs") / f"{review_base}_llm_review.txt"
    if review_path.exists():
        result["llm_review_txt_path"] = str(review_path)
        try:
            with open(review_path, "r", encoding="utf-8") as f:
                result["llm_review_text"] = f.read()
        except Exception:
            pass

def _prepare_result_for_pdf(result: dict) -> dict:
    r = dict(result)
    for k in ("original_image", "header_json", "full_text_json", "table_crop_image", "llm_review_txt_path"):
        if r.get(k):
            r[k] = _as_fs(r[k])
    if r.get("table_csvs"):
        r["table_csvs"] = [_as_fs(p) for p in r["table_csvs"] if p]
    if r.get("tables"):
        r["tables"] = [{**t, "image": _as_fs(t.get("image")) if t.get("image") else None} for t in r["tables"]]
    return r

def _first_existing(cands: list[str]) -> str | None:
    for c in cands:
        if Path(c).exists():
            return c
    return None

def _payload_stats(review_base: str) -> dict:
    out = {"full_text_chars": 0, "csv_lines": 0, "warnings": 0}
    ft = _first_existing([
        f"outputs/{review_base}_full_text.json",
        f"outputs/{review_base}_page1_full_text.json",
        f"outputs/{review_base}_ocr.json",
    ])
    if ft and Path(ft).exists():
        try:
            raw = Path(ft).read_text(encoding="utf-8")
            out["full_text_chars"] = len(raw)
        except Exception:
            pass
    csvp = _first_existing([
        f"outputs/{review_base}_table_0.csv",
        f"outputs/{review_base}_page1_table_0.csv",
    ])
    if csvp and Path(csvp).exists():
        try:
            out["csv_lines"] = sum(1 for _ in open(csvp, "r", encoding="utf-8"))
        except Exception:
            pass
    wp = _first_existing([
        f"outputs/{review_base}_warnings.json",
        f"outputs/{review_base}_warn.json",
    ])
    if wp and Path(wp).exists():
        try:
            w = json.loads(Path(wp).read_text(encoding="utf-8"))
            if isinstance(w, dict) and "warnings" in w:
                out["warnings"] = len(w["warnings"])
            elif isinstance(w, list):
                out["warnings"] = len(w)
            else:
                out["warnings"] = 1
        except Exception:
            pass
    return out

def _ping_llm(timeout_s: float = 5.0) -> dict:
    url = _llm_base_url().rstrip("/") + "/v1/models"
    t0 = time.time()
    try:
        r = requests.get(url, timeout=timeout_s)
        r.raise_for_status()
        dt = time.time() - t0
        models = r.json()
        return {"ok": True, "latency_s": round(dt, 3), "count": len(models.get("data", [])), "url": url}
    except Exception as e:
        return {"ok": False, "latency_s": None, "error": str(e), "url": url}

# Pretty stage logger (prints + accumulates for response)
def _mk_logger():
    lines: list[str] = []
    def _log(msg: str):
        line = f"{time.strftime('%H:%M:%S')}  {msg}"
        print(line)
        lines.append(line)
    return _log, lines

# ──────────────────────────────────────────────────────────────────────────────
# Health: ping / warmup / speedtest
# ──────────────────────────────────────────────────────────────────────────────
@app.get("/llm/ping")
def llm_ping():
    return _ping_llm()

@app.post("/llm/warmup")
def llm_warmup():
    """Send a tiny request to keep the model warm."""
    url = _llm_base_url().rstrip("/") + "/v1/chat/completions"
    payload = {
        "model": os.getenv("LLM_MODEL", "mistral"),
        "messages": [{"role": "user", "content": "Reply with OK and stop."}],
        "max_tokens": 4, "temperature": 0.0, "stream": False
    }
    t0 = time.time()
    try:
        r = requests.post(url, json=payload, timeout=(5, 15))
        r.raise_for_status()
        dt = time.time() - t0
        return {"ok": True, "latency_s": round(dt, 3)}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/llm/speedtest")
def llm_speedtest(max_tokens: int = Query(160, ge=16, le=512)):
    url = _llm_base_url().rstrip("/") + "/v1/chat/completions"
    payload = {
        "model": os.getenv("LLM_MODEL", "mistral"),
        "messages": [{"role": "user", "content": "Write 'x' repeatedly."}],
        "max_tokens": max_tokens, "temperature": 0.0, "stream": False
    }
    t0 = time.time()
    try:
        r = requests.post(url, json=payload, timeout=(5, 60 + max_tokens // 2))
        r.raise_for_status()
        dt = time.time() - t0
        text = r.json()["choices"][0]["message"]["content"]
        toks = len(text.split())
        return {"ok": True, "elapsed_s": round(dt, 2), "approx_tokens": toks}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ──────────────────────────────────────────────────────────────────────────────
# Main API
# ──────────────────────────────────────────────────────────────────────────────
@app.post("/process")
async def process_document(
    file: UploadFile = File(...),
    translate_headers: bool = Query(False, description="Map headers to canonical names"),
    validate_schema: bool = Query(True,  description="Run validation rules"),
    generate_pdf:   bool = Query(True,  description="Generate PDF report"),
    run_llm_review: bool = Query(False,  description="Run LLM review before PDF"),
):
    log, log_lines = _mk_logger()
    try:
        T0 = time.time()

        # 1) Save upload
        input_filename = f"uploads/{uuid.uuid4().hex}_{file.filename}"
        log(f"STEP 1/5  Saving upload → {input_filename}")
        with open(input_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        log(f"OK: upload saved.")

        # 2) YOLO + OCR + parsing
        extractor.translate_headers = bool(translate_headers)
        extractor.validate = bool(validate_schema)

        log("STEP 2/5  YOLO table detection + OCR running…")
        t_ex0 = time.time()
        result = extractor.process(input_filename)
        t_ex1 = time.time()
        log(f"OK: extraction finished in {t_ex1 - t_ex0:.2f}s")

        # Quick detection summary
        n_tables = len(result.get("tables", []) or [])
        log(f"DETECT: tables found = {n_tables}")
        if n_tables:
            for t in result["tables"]:
                shape = t.get("shape") or "?"
                img = t.get("image")
                log(f"  • table {t.get('index')}: shape={shape}  image={img}")

        base_name = os.path.splitext(os.path.basename(input_filename))[0]

        # 3) Copy original for UI
        output_original_path = os.path.join("outputs", os.path.basename(input_filename))
        shutil.copy(input_filename, output_original_path)
        log(f"FILE: original image copied → {output_original_path}")

        # Artifact presence messages
        def _say_generated(label: str, p: str | None):
            if not p: return
            fs = _as_fs(p)
            if fs and Path(fs).exists():
                log(f"FILE: {label} generated → {fs}")

        _say_generated("header_json", result.get("header_json"))
        _say_generated("full_text_json", result.get("full_text_json"))
        _say_generated("table_crop_image", result.get("table_crop_image"))

        for p in (result.get("table_csvs") or []):
            _say_generated("table_csv", p)

        if not result.get("original_image"):
            result["original_image"] = output_original_path

        # 4) LLM review BEFORE PDF (optional)
        review_base = _detect_review_base(base_name) or base_name
        if run_llm_review:
            log("STEP 3/5  LLM review… running")
            ping = _ping_llm()
            log(f"LLM: ping → {ping}")

            stats = _payload_stats(review_base)
            log(f"LLM: payload stats → {stats}")

            t_llm0 = time.time()
            try:
                rr = do_run_review(
                    outputs_dir="outputs",
                    base=review_base,
                    llm_base_url=_llm_base_url(),
                    model=os.getenv("LLM_MODEL") or "mistral",
                    temperature=0.2,
                    force=False,
                )
                _attach_llm_review_to_result(result, review_base)
                log(f"OK: LLM review finished in {time.time() - t_llm0:.2f}s")
                _say_generated("llm_review_txt", f"outputs/{review_base}_llm_review.txt")
            except Exception as e:
                log(f"WARN: LLM review failed → {e}")
                try:
                    Path(f"outputs/{review_base}_llm_review.txt").write_text(
                        "(LLM review skipped due to error/timeout)", encoding="utf-8"
                    )
                    result["llm_review_txt_path"] = f"outputs/{review_base}_llm_review.txt"
                    _say_generated("llm_review_txt (placeholder)", f"outputs/{review_base}_llm_review.txt")
                except Exception:
                    pass
        else:
            Path(f"outputs/{review_base}_llm_review.txt").write_text("(LLM review skipped)", encoding="utf-8")
            result["llm_review_txt_path"] = f"outputs/{review_base}_llm_review.txt"
            _say_generated("llm_review_txt (skipped)", f"outputs/{review_base}_llm_review.txt")

        # 5) warnings.json (if any)
        warn_path = Path("outputs") / f"{review_base}_warnings.json"
        if warn_path.exists():
            result["warnings_json"] = str(warn_path)
            log(f"FILE: warnings_json generated → {warn_path}")

        # 6) PDF
        if generate_pdf:
            log("STEP 4/5  PDF report… generating")
            t_pdf0 = time.time()
            pdf_path = os.path.join("outputs", f"{base_name}_report.pdf")
            result_for_pdf = _prepare_result_for_pdf(result)
            generate_pdf_report(result_for_pdf, pdf_path)
            result["report_pdf"] = pdf_path
            log(f"OK: PDF generated → {pdf_path}  in {time.time() - t_pdf0:.2f}s")

        # 7) Prepare URLs and return
        result["original_image"]   = _to_url(result.get("original_image") or output_original_path)
        result["header_json"]      = _to_url(result.get("header_json"))
        result["full_text_json"]   = _to_url(result.get("full_text_json"))
        result["table_crop_image"] = _to_url(result.get("table_crop_image"))
        result["table_csvs"]       = [_to_url(p) for p in result.get("table_csvs", []) if p]
        if result.get("llm_review_txt_path"):
            result["llm_review_txt"] = _to_url(result["llm_review_txt_path"])
        if result.get("warnings_json"):
            result["warnings_json"] = _to_url(result["warnings_json"])
        if result.get("report_pdf"):
            result["report_pdf"] = _to_url(result["report_pdf"])

        log("STEP 5/5  DONE ✅  (see outputs/ for artifacts)")
        log(f"TOTAL: {time.time() - T0:.2f}s")

        # expose logs to UI if needed
        result["log_lines"] = log_lines

        # Also pretty-print once to server console
        pprint.pprint(result)
        return JSONResponse(content=result)

    except Exception as e:
        print("❌ Extraction failed:")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

# Re-run/cached review
@app.get("/review")
def review_endpoint(
    base: str = Query(..., description="Base name (e.g. '<upload>' or '<upload>_page1')."),
    model: str = Query("mistral", description="Model ID on your local server."),
    temperature: float = Query(0.2, ge=0.0, le=1.0),
    force: bool = Query(False, description="Force re-generate (bypass cache)"),
):
    t0 = time.time()
    res = do_run_review(
        outputs_dir="outputs",
        base=base,
        llm_base_url=_llm_base_url(),
        model=model,
        temperature=temperature,
        force=force,
    )
    print(f"[TIMING] /review call: {time.time() - t0:.2f}s")
    status = 200 if "error" not in res else 500
    return JSONResponse(content=res, status_code=status)

# Bundle all artifacts
@app.get("/zip")
def download_zip():
    zip_path = "outputs/results.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for root, _, files in os.walk("outputs"):
            for file in files:
                if file.endswith((".csv", ".json", ".png", ".txt", ".pdf")):
                    zipf.write(os.path.join(root, file), arcname=file)
    return FileResponse(zip_path, filename="processed_results.zip")
