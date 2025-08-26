# backend/pdf_report.py
'''
# Old Script 

import os
import json
from datetime import datetime
from collections import defaultdict, Counter

import pdfkit
import pandas as pd
from jinja2 import Environment, FileSystemLoader


# ----------------------------
# Path + URL helpers (tolerant)
# ----------------------------

def _outputs_path(url_or_path) -> str:
     
    if not url_or_path:  # None or empty
        return ""
    s = str(url_or_path).replace("\\", "/")

    # If it's already a web URL with /outputs/
    if "/outputs/" in s:
        name = s.split("/outputs/")[-1]
        return os.path.abspath(os.path.join("outputs", name))

    # If it's just a filename (no slash), treat it as a file in outputs/
    if "/" not in s:
        return os.path.abspath(os.path.join("outputs", os.path.basename(s)))

    # Else, assume it's a real filesystem path (absolute or relative)
    return os.path.abspath(s)


def _as_file_url(path: str) -> str:
    """Convert absolute path to file:// URL for wkhtmltopdf."""
    if not path:
        return ""
    return f"file:///{path.replace(os.sep, '/')}"


# ----------------------------
# Data loading helpers
# ----------------------------

def _load_header_json(header_json_url: str) -> dict:
    p = _outputs_path(header_json_url)
    if p and os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}
 
def _load_full_text(full_text_json_url: str) -> str:
    p = _outputs_path(full_text_json_url)
    if not p or not os.path.exists(p):
        return "No OCR text available."

    try:
        with open(p, "r", encoding="utf-8") as f:
            raw = f.read()

        # Try to parse JSON first
        try:
            obj = json.loads(raw)
            if isinstance(obj, dict) and "text" in obj:
                return obj["text"] or ""
            if isinstance(obj, (list, dict)):
                return json.dumps(obj, indent=2, ensure_ascii=False)
            return str(obj)  # JSON scalar
        except json.JSONDecodeError:
            # Not JSON → return raw text (old extractor behavior)
            return raw
    except Exception:
        return "No OCR text available."


def _load_tables(csv_urls: list) -> list:
    
    out = []
    for url in (csv_urls or []):
        if not url:
            continue
        p = _outputs_path(url)
        if not p or not os.path.exists(p):
            continue
        try:
            df = pd.read_csv(p, dtype=str).fillna("")
            headers = list(df.columns)
            rows = df.values.tolist()
            out.append({"headers": headers, "rows": rows, "csv_path": p})
        except Exception as e:
            # Fallback to raw lines if pandas fails
            try:
                with open(p, "r", encoding="utf-8") as f:
                    lines = [ln.rstrip("\n") for ln in f]
                if lines:
                    headers = lines[0].split(",")
                    rows = [ln.split(",") for ln in lines[1:]]
                    out.append({"headers": headers, "rows": rows, "csv_path": p})
            except Exception:
                print(f"[pdf_report] skip unreadable CSV: {p} ({e})")
                continue
    return out


def _map_table_images(data: dict) -> dict:
    
    img_map = {}

    # Structured list (if present)
    for t in (data.get("tables") or []):
        idx = t.get("index")
        img_ref = t.get("image")
        if idx is None or not img_ref:
            continue
        p = _outputs_path(img_ref)
        if p and os.path.exists(p):
            img_map[int(idx)] = _as_file_url(os.path.abspath(p))

    # Fallback: single first crop
    if not img_map and data.get("table_crop_image"):
        p = _outputs_path(data["table_crop_image"])
        if p and os.path.exists(p):
            img_map[0] = _as_file_url(os.path.abspath(p))

    return img_map

# ----------------------------
# Validation summary rendering
# ----------------------------

def _split_warnings(warnings: list):
    """Split validation warnings into header_warnings and table_warnings."""
    header_w = []
    table_w = []
    for w in warnings or []:
        if "header_warning" in w:
            header_w.append(w["header_warning"])
        elif "table" in w and w["table"] is not None:
            table_w.append(w)
    return header_w, table_w


def _build_validation_summary_html(warnings: list, table_img_map: dict) -> str:
    """
    Create an HTML block with:
      - total warnings
      - per-table counts
      - top 3 recurring issues per table
      - table image preview (if available)
    """
    header_warnings, table_warnings = _split_warnings(warnings)

    total = len(warnings or [])
    tables = defaultdict(list)
    for w in table_warnings:
        tables[int(w.get("table", -1))].append(w)

    html = []
    html.append(f"""
<section style="margin:24px 0; font-family: Arial, Helvetica, sans-serif;">
  <h2 style="margin:0 0 8px 0; font-size:18px;">Validation Summary</h2>
  <div style="display:flex; gap:12px; flex-wrap:wrap; margin-bottom:12px;">
    <div style="background:#f4f6f8; padding:8px 12px; border-radius:8px;">Total warnings: <b>{total}</b></div>
    <div style="background:#f4f6f8; padding:8px 12px; border-radius:8px;">Tables with warnings: <b>{len(tables)}</b></div>
  </div>
""")

    # Header warnings
    if header_warnings:
        html.append('<div style="margin:10px 0 14px 0;"><b>Header warnings</b><ul style="margin:6px 0 0 18px;">')
        for hw in header_warnings:
            html.append(f"<li>{hw}</li>")
        html.append("</ul></div>")

    # Per-table details
    for t_idx in sorted(tables.keys()):
        ws = tables[t_idx]
        count = len(ws)
        # Top messages by frequency (message text only)
        msg_counter = Counter(w.get("message", "Issue") for w in ws)
        top_msgs = [m for m, _c in msg_counter.most_common(3)]

        # Distinct rows and fields (optional quick stats)
        rows_set = {w.get("row") for w in ws if w.get("row") is not None}
        fields_set = {w.get("field") for w in ws if w.get("field")}

        # Card header
        html.append(f"""
  <div style="border:1px solid #e6e9ec; border-radius:8px; padding:12px; margin:10px 0;">
    <div style="display:flex; align-items:center; gap:12px; justify-content:space-between; flex-wrap:wrap;">
      <div>
        <div style="font-weight:600;">Table {t_idx}</div>
        <div style="color:#444; font-size:12px;">Warnings: <b>{count}</b> · Rows affected: <b>{len(rows_set)}</b> · Fields: <b>{len(fields_set)}</b></div>
      </div>
""")
        # Image preview if we have one
        img_url = table_img_map.get(t_idx)
        if img_url:
            html.append(f"""
      <div style="margin-left:auto;">
        <img src="{img_url}" style="max-height:140px; border:1px solid #ddd; border-radius:6px;" />
      </div>
""")
        html.append("</div>")  # header line

        # Top recurring messages
        if top_msgs:
            html.append('<ul style="margin:10px 0 0 18px;">')
            for m in top_msgs:
                html.append(f"<li>{m}</li>")
            html.append("</ul>")

        html.append("</div>")  # card

    html.append("</section>")
    return "".join(html)


# ----------------------------
# Main report entry point
# ----------------------------

def generate_pdf_report(data: dict, output_path: str):
    # Jinja environment
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("report_template.html")

    # Original page image (optional)
    image_url = ""
    if data.get("original_image"):
        p = _outputs_path(data["original_image"])
        if p and os.path.exists(p):
            image_url = _as_file_url(os.path.abspath(p))

    # Header / Full OCR text
    header_info = _load_header_json(data.get("header_json"))
    full_text = _load_full_text(data.get("full_text_json"))

    # Tables (CSV) and images map
    tables = _load_tables(data.get("table_csvs"))
    table_img_map = _map_table_images(data)

    # Warnings + validation summary
    warnings = data.get("warnings", [])
    validation_summary_html = _build_validation_summary_html(warnings, table_img_map)

    # LLM Review (optional)
    llm_review = ""
    if data.get("llm_review_txt"):
        p = _outputs_path(data["llm_review_txt"])
        if p and os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                llm_review = f.read()

    # Render template
    html_out = template.render(
        image_url=image_url,
        header=header_info,
        full_text=full_text,
        tables=tables,                # [{headers, rows, csv_path}]
        warnings=warnings,            # raw warnings list (kept for backward compatibility)
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        model_name="mistral",
        version="v1.1",
        llm_review=llm_review,
    )

    # Inject Validation Summary block before </body> (template stays unchanged)
    if "</body>" in html_out:
        html_out = html_out.replace("</body>", validation_summary_html + "</body>")
    else:
        html_out += validation_summary_html

    # Generate PDF (configure wkhtmltopdf path if needed)
    # Example for Windows:
    # config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    config = pdfkit.configuration()
    options = {"enable-local-file-access": None}
    pdfkit.from_string(html_out, output_path, configuration=config, options=options)
'''

# backend/pdf_report.py

import os
import json
import re
from datetime import datetime
from collections import defaultdict, Counter
from pathlib import Path

import pdfkit
import pandas as pd
from jinja2 import Environment, FileSystemLoader

# ----------------------------
# Path + URL helpers (tolerant)
# ----------------------------

def _outputs_path(url_or_path) -> str:
    """Return an absolute filesystem path under outputs/ if given a /outputs URL or bare filename."""
    if not url_or_path:
        return ""
    s = str(url_or_path).replace("\\", "/")

    # If it's already a web URL with /outputs/
    if "/outputs/" in s:
        name = s.split("/outputs/")[-1]
        return os.path.abspath(os.path.join("outputs", name))

    # If it's just a filename (no slash), treat it as a file in outputs/
    if "/" not in s:
        return os.path.abspath(os.path.join("outputs", os.path.basename(s)))

    # Else, assume it's a real filesystem path (absolute or relative)
    return os.path.abspath(s)


def _as_file_url(path: str) -> str:
    """Convert absolute path to file:// URL for wkhtmltopdf."""
    if not path:
        return ""
    return f"file:///{path.replace(os.sep, '/')}"


# ----------------------------
# Data loading helpers
# ----------------------------

def _load_header_json(header_json_url: str) -> dict:
    p = _outputs_path(header_json_url)
    if p and os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _load_full_text(full_text_json_url: str) -> str:
    p = _outputs_path(full_text_json_url)
    if not p or not os.path.exists(p):
        return "No OCR text available."

    try:
        with open(p, "r", encoding="utf-8") as f:
            raw = f.read()

        # Try to parse JSON first
        try:
            obj = json.loads(raw)
            if isinstance(obj, dict) and "text" in obj:
                return obj["text"] or ""
            if isinstance(obj, (list, dict)):
                return json.dumps(obj, indent=2, ensure_ascii=False)
            return str(obj)  # JSON scalar
        except json.JSONDecodeError:
            # Not JSON → return raw text (old extractor behavior)
            return raw
    except Exception:
        return "No OCR text available."


def _load_tables(csv_urls: list) -> list:
    out = []
    for url in (csv_urls or []):
        if not url:
            continue
        p = _outputs_path(url)
        if not p or not os.path.exists(p):
            continue
        try:
            df = pd.read_csv(p, dtype=str).fillna("")
            headers = list(df.columns)
            rows = df.values.tolist()
            out.append({"headers": headers, "rows": rows, "csv_path": p})
        except Exception as e:
            # Fallback to raw lines if pandas fails
            try:
                with open(p, "r", encoding="utf-8") as f:
                    lines = [ln.rstrip("\n") for ln in f]
                if lines:
                    headers = lines[0].split(",")
                    rows = [ln.split(",") for ln in lines[1:]]
                    out.append({"headers": headers, "rows": rows, "csv_path": p})
            except Exception:
                print(f"[pdf_report] skip unreadable CSV: {p} ({e})")
                continue
    return out


def _map_table_images(data: dict) -> dict:
    """Return {table_index: file:// URL} for crop previews."""
    img_map = {}

    # Structured list (if present)
    for t in (data.get("tables") or []):
        idx = t.get("index")
        img_ref = t.get("image")
        if idx is None or not img_ref:
            continue
        p = _outputs_path(img_ref)
        if p and os.path.exists(p):
            img_map[int(idx)] = _as_file_url(os.path.abspath(p))

    # Fallback: single first crop
    if not img_map and data.get("table_crop_image"):
        p = _outputs_path(data["table_crop_image"])
        if p and os.path.exists(p):
            img_map[0] = _as_file_url(os.path.abspath(p))

    return img_map


# ----------------------------
# LLM review helpers (robust)
# ----------------------------

def _infer_base_from_header(data: dict) -> str | None:
    """Derive '<base>' from header_json like '<base>_header.json'."""
    p = _outputs_path((data or {}).get("header_json"))
    if not p:
        return None
    fname = os.path.basename(p)
    return fname[:-len("_header.json")] if fname.endswith("_header.json") else None


def _get_review_text(data: dict) -> str | None:
    """
    Prefer in-memory text; else read from llm_review_txt_path or llm_review_txt (path or /outputs URL);
    else infer <base> from header and try common filenames.
    """
    if not isinstance(data, dict):
        return None

    # 1) in-memory
    t = data.get("llm_review_text")
    if t:
        return t

    # 2) explicit path/url fields
    for k in ("llm_review_txt_path", "llm_review_txt"):
        if k in data and data[k]:
            p = _outputs_path(data[k])
            if p and os.path.exists(p):
                try:
                    return open(p, "r", encoding="utf-8").read()
                except Exception:
                    pass

    # 3) infer from header base
    base = _infer_base_from_header(data)
    if base:
        candidates = [
            f"outputs/{base}_llm_review.txt",
            f"outputs/{base}_page1_llm_review.txt",
        ]
        # last resort: any file that starts with base and ends with _llm_review.txt
        candidates.extend(str(p) for p in Path("outputs").glob(f"{base}*_llm_review.txt"))
        for cand in candidates:
            if os.path.exists(cand):
                try:
                    return open(cand, "r", encoding="utf-8").read()
                except Exception:
                    continue

    return None


# ----------------------------
# Validation summary rendering
# ----------------------------

def _split_warnings(warnings: list):
    """Split validation warnings into header_warnings and table_warnings."""
    header_w = []
    table_w = []
    for w in warnings or []:
        if "header_warning" in w:
            header_w.append(w["header_warning"])
        elif "table" in w and w.get("table") is not None:
            table_w.append(w)
    return header_w, table_w


def _build_validation_summary_html(warnings: list, table_img_map: dict) -> str:
    """
    Create an HTML block with:
      - total warnings
      - per-table counts
      - top 3 recurring issues per table
      - table image preview (if available)
    """
    header_warnings, table_warnings = _split_warnings(warnings)

    total = len(warnings or [])
    tables = defaultdict(list)
    for w in table_warnings:
        tables[int(w.get("table", -1))].append(w)

    html = []
    html.append(f"""
<section style="margin:24px 0; font-family: Arial, Helvetica, sans-serif;">
  <h2 style="margin:0 0 8px 0; font-size:18px;">Validation Summary</h2>
  <div style="display:flex; gap:12px; flex-wrap:wrap; margin-bottom:12px;">
    <div style="background:#f4f6f8; padding:8px 12px; border-radius:8px;">Total warnings: <b>{total}</b></div>
    <div style="background:#f4f6f8; padding:8px 12px; border-radius:8px;">Tables with warnings: <b>{len(tables)}</b></div>
  </div>
""")

    # Header warnings
    if header_warnings:
        html.append('<div style="margin:10px 0 14px 0;"><b>Header warnings</b><ul style="margin:6px 0 0 18px;">')
        for hw in header_warnings:
            html.append(f"<li>{hw}</li>")
        html.append("</ul></div>")

    # Per-table details
    for t_idx in sorted(tables.keys()):
        ws = tables[t_idx]
        count = len(ws)
        # Top messages by frequency (message text only)
        msg_counter = Counter(w.get("message", "Issue") for w in ws)
        top_msgs = [m for m, _c in msg_counter.most_common(3)]

        # Distinct rows and fields (optional quick stats)
        rows_set = {w.get("row") for w in ws if w.get("row") is not None}
        fields_set = {w.get("field") for w in ws if w.get("field")}

        # Card header
        html.append(f"""
  <div style="border:1px solid #e6e9ec; border-radius:8px; padding:12px; margin:10px 0;">
    <div style="display:flex; align-items:center; gap:12px; justify-content:space-between; flex-wrap:wrap;">
      <div>
        <div style="font-weight:600;">Table {t_idx}</div>
        <div style="color:#444; font-size:12px;">Warnings: <b>{count}</b> · Rows affected: <b>{len(rows_set)}</b> · Fields: <b>{len(fields_set)}</b></div>
      </div>
""")
        # Image preview if we have one
        img_url = table_img_map.get(t_idx)
        if img_url:
            html.append(f"""
      <div style="margin-left:auto;">
        <img src="{img_url}" style="max-height:140px; border:1px solid #ddd; border-radius:6px;" />
      </div>
""")
        html.append("</div>")  # header line

        # Top recurring messages
        if top_msgs:
            html.append('<ul style="margin:10px 0 0 18px;">')
            for m in top_msgs:
                html.append(f"<li>{m}</li>")
            html.append("</ul>")

        html.append("</div>")  # card

    html.append("</section>")
    return "".join(html)


# ----------------------------
# Main report entry point
# ----------------------------

 
 
def generate_pdf_report(data: dict, output_path: str):
    # Jinja environment
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("report_template.html")

    # Original page image (optional)
    image_url = ""
    if data.get("original_image"):
        p = _outputs_path(data["original_image"])
        if p and os.path.exists(p):
            image_url = _as_file_url(os.path.abspath(p))

    # Header / Full OCR text
    header_info = _load_header_json(data.get("header_json"))
    full_text = _load_full_text(data.get("full_text_json"))

    # Tables (CSV) and images map
    tables = _load_tables(data.get("table_csvs"))
    table_img_map = _map_table_images(data)

    # Warnings + validation summary
    warnings = data.get("warnings", [])
    validation_summary_html = _build_validation_summary_html(warnings, table_img_map)

    # LLM Review (robust: from memory, from explicit path/url, or inferred)
    llm_review = _get_review_text(data) or "No LLM review available."

    # Render template (now passing validation_summary_html directly)
    html_out = template.render(
        image_url=image_url,
        header=header_info,
        full_text=full_text,
        tables=tables,                # [{headers, rows, csv_path}]
        warnings=warnings,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        model_name="mistral",
        version="v1.2",
        llm_review=llm_review,
        validation_summary_html=validation_summary_html,  # <<< NEW
    )

    # Generate PDF (configure wkhtmltopdf path if needed)
    config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)# add path to wkhtmltopdf here if required
    options = {
        "enable-local-file-access": None,
        "encoding": "UTF-8",
        # keep any other options you were using (dpi, image-quality, quiet, etc.)
    }
    pdfkit.from_string(html_out, output_path, configuration=config, options=options)
