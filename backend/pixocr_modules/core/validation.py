# backend/core/validation.py
'''

import json
import re
from typing import List, Dict, Any

import pandas as pd
from jsonschema import Draft7Validator

# --- JSON Schema (kept lightweight; we coerce values before validating)
schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "position": {"type": ["integer", "null"]},
        "quantity": {"type": ["number", "null"]},
        "diameter_mm": {"type": ["number", "null"]},
        "unit_length_m": {"type": ["number", "null"]},
        "total_length_m": {"type": ["number", "null"]},
        "weight_kg": {"type": ["number", "null"]},
    },
    "required": ["quantity"],
    "additionalProperties": True
}
validator = Draft7Validator(schema)

# --- Optional: spaCy if available, but we won't require it
try:
    import spacy
    nlp = spacy.load("de_core_news_sm")
except Exception:
    nlp = None


NUM_COLS = ["quantity", "diameter_mm", "unit_length_m", "total_length_m", "weight_kg"]
INT_COLS = ["position"]


def _to_float(s):
    """Coerce value to float; handles '4,78' -> 4.78 and strips junk."""
    if pd.isna(s):
        return None
    x = str(s).strip()
    if not x:
        return None
    # keep only first number pattern
    m = re.search(r"[-+]?\d+(?:[.,]\d+)?", x)
    if not m:
        return None
    x = m.group(0).replace(",", ".")
    try:
        return float(x)
    except Exception:
        return None


def _to_int(s):
    """Coerce value to int if it looks integer-like."""
    f = _to_float(s)
    if f is None:
        return None
    try:
        return int(round(f))
    except Exception:
        return None


def _coerce_df(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in NUM_COLS:
        if c in out.columns:
            out[c] = out[c].map(_to_float)
    for c in INT_COLS:
        if c in out.columns:
            out[c] = out[c].map(_to_int)
    return out


def _validate_row_domain(row: Dict[str, Any], idx: int, table_i: int) -> List[Dict[str, Any]]:
    w = []

    # Basic non-negativity and presence
    q = row.get("quantity")
    if q is not None and q <= 0:
        w.append(_warn(table_i, idx, "quantity", "Quantity should be > 0."))

    for c in ["diameter_mm", "unit_length_m", "total_length_m", "weight_kg"]:
        v = row.get(c)
        if v is not None and v < 0:
            w.append(_warn(table_i, idx, c, f"{c} should be non-negative."))

    # Reasonable diameter range (rebars typically ~6–40 mm)
    d = row.get("diameter_mm")
    if d is not None and not (4 <= d <= 50):
        w.append(_warn(table_i, idx, "diameter_mm", "Unusual diameter (expected 4–50 mm)."))

    # Length consistency: total ≈ unit * quantity
    ulen = row.get("unit_length_m")
    tlen = row.get("total_length_m")
    if q is not None and ulen is not None and tlen is not None:
        pred = q * ulen
        # relative tolerance 5% or absolute 0.02 m (whichever larger)
        tol = max(0.05 * pred, 0.02)
        if abs(tlen - pred) > tol:
            w.append(_warn(
                table_i, idx, "total_length_m",
                f"Total length ({tlen}) not consistent with quantity*unit_length ({pred:.3f})."
            ))

    # Weight sanity: weight ≈ (d^2 / 162) * total_length
    # (classic rebar formula; d in mm, weight in kg)
    if d is not None and tlen is not None and row.get("weight_kg") is not None:
        kg_per_m = (d ** 2) / 162.0
        pred_w = kg_per_m * tlen
        w_val = row.get("weight_kg")
        # allow generous 10% tolerance
        tol_w = max(0.10 * pred_w, 0.05)
        if abs(w_val - pred_w) > tol_w:
            w.append(_warn(
                table_i, idx, "weight_kg",
                f"Weight ({w_val}) differs from expected ({pred_w:.3f}) for Ø={d}mm."
            ))

    return w


def _warn(table_i: int, row_i: int, field: str, message: str) -> Dict[str, Any]:
    return {"table": table_i, "row": row_i + 1, "field": field, "message": message}


def _header_warnings(header: Dict[str, Any]) -> List[Dict[str, Any]]:
    w = []
    # Direct key presence (these keys are produced by your header key_map)
    must_keys = ["PROJECT", "PERSON", "DATE"]
    for k in must_keys:
        if not header.get(k):
            w.append({"header_warning": f"Missing {k} in header"})

    # DATE plausibility via regex if value exists
    date_val = header.get("DATE")
    if date_val:
        # Accept dd.mm.yyyy, dd/mm/yyyy, yyyy-mm-dd, etc.
        if not re.search(r"\b(\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2}|\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})\b", str(date_val)):
            w.append({"header_warning": f"DATE value looks unusual: {date_val}"})

    # Optional NER fallback if spaCy available (non-blocking)
    if nlp is not None:
        try:
            raw = "\n".join([f"{k}: {v}" for k, v in header.items() if v])
            doc = nlp(raw)
            labels = {ent.label_ for ent in doc.ents}
            # If PERSON is still missing and we didn't see any PERSON entities
            if not header.get("PERSON") and "PER" not in labels and "PERSON" not in labels:
                w.append({"header_warning": "PERSON not detected in header text (NER)."})
        except Exception:
            pass

    return w


def run_validations(table_csvs: List[str], header_data: dict, cfg) -> List[Dict[str, Any]]:
    warnings: List[Dict[str, Any]] = []

    for i, path in enumerate(table_csvs):
        try:
            df = pd.read_csv(path)
        except Exception as e:
            warnings.append({"table": i, "row": None, "field": None, "message": f"Cannot read CSV: {e}"})
            continue

        if df.empty:
            warnings.append({"table": i, "row": None, "field": None, "message": "Empty table."})
            continue

        # Ensure canonical columns are present if extractor missed mapping
        # (No rename performed here; we validate only columns that already exist)
        df = _coerce_df(df)

        # First pass: JSON Schema (after coercion) for each row
        for row_idx, row in df.iterrows():
            row_dict = row.to_dict()
            for err in validator.iter_errors(row_dict):
                warnings.append({
                    "table": i,
                    "row": row_idx + 1,
                    "field": list(err.path)[0] if err.path else None,
                    "message": err.message
                })

        # Second pass: domain-specific checks
        for row_idx, row in df.iterrows():
            warnings.extend(_validate_row_domain(row.to_dict(), row_idx, i))

    # Header checks
    warnings.extend(_header_warnings(header_data or {}))

    return warnings
'''

# core/validation.py
from __future__ import annotations
import os, re, json
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

# --- Optional JSON Schema (if table_schema.json exists)
try:
    from jsonschema import Draft7Validator
except Exception:
    Draft7Validator = None

# ----------------------------
# Path & config helpers
# ----------------------------
def _fs_from_outputs_url(p: str | None) -> str | None:
    if not p: return None
    s = str(p)
    if s.startswith("/outputs/"): s = s[len("/outputs/"):]
    cand = Path("outputs") / Path(s).name
    if cand.exists(): return str(cand)
    return s if Path(s).exists() else None

def _read_cfg_path(cfg, path: List[str], default=None):
    cur = cfg
    for key in path:
        if cur is None: return default
        if isinstance(cur, dict):
            cur = cur.get(key, None)
        else:
            cur = getattr(cur, key, None)
    return default if cur is None else cur

def _infer_base_from_csv(csv_path: str | None) -> str | None:
    p = _fs_from_outputs_url(csv_path)
    if not p: return None
    name = Path(p).name
    # strip _table_0_val.csv or _table_0.csv
    for suf in ["_table_0_val.csv", "_table_0.csv"]:
        if name.endswith(suf): return name[:-len(suf)]
    # last resort: strip .csv
    return name[:-4] if name.endswith(".csv") else None

# ----------------------------
# Parsing helpers
# ----------------------------
_NUM = re.compile(r"^\s*[+-]?\d+(?:[.,]\d+)?\s*$")

def _to_float(x) -> Optional[float]:
    if x is None: return None
    s = str(x).strip().replace(" ", "")
    if not _NUM.match(s): return None
    try: return float(s.replace(",", "."))
    except: return None

def _to_int(x) -> Optional[int]:
    if x is None: return None
    try: return int(str(x).strip())
    except:
        f = _to_float(x)
        return int(round(f)) if f is not None else None

def _kg_per_m(d_mm: Optional[int | float]) -> Optional[float]:
    if d_mm is None: return None
    try:
        d = float(d_mm)
        return (d*d)/162.0
    except: return None

# ----------------------------
# Loaders
# ----------------------------
def _load_csv(path_like: str | None) -> pd.DataFrame:
    p = _fs_from_outputs_url(path_like)
    if not p or not os.path.exists(p): return pd.DataFrame()
    try:
        return pd.read_csv(p, dtype=str).fillna("")
    except Exception:
        return pd.DataFrame()

def _load_full_text_json(base: str | None) -> str | None:
    if not base: return None
    for cand in [f"outputs/{base}_full_text.json", f"outputs/{base}_page1_full_text.json"]:
        if os.path.exists(cand):
            try:
                with open(cand, "r", encoding="utf-8") as f:
                    raw = f.read()
                try:
                    obj = json.loads(raw)
                    # Accept list of blocks or dict{"text":...}
                    if isinstance(obj, dict) and "text" in obj:
                        return str(obj["text"])
                    return json.dumps(obj, ensure_ascii=False)
                except json.JSONDecodeError:
                    return raw
            except Exception:
                return None
    return None

# ----------------------------
# OCR totals extraction (optional, tolerant)
# ----------------------------
_RX_NUM = r"([0-9]+(?:[.,][0-9]+)?)"
def _find_num(pattern: str, text: str) -> Optional[float]:
    m = re.search(pattern, text, flags=re.I)
    if not m: return None
    return _to_float(m.group(1))

def _extract_totals_from_ocr(ocr_text: str) -> Dict[str, Optional[float]]:
    """
    Looks for:
      - Gesamtgewicht ... <kg>
      - Anzahl der Ausführungen ... <int>
      - Summe ... (total length or weight lines)
    Returns dict with keys: total_weight_kg, total_quantity, total_length_m (if any).
    """
    if not ocr_text: return {}
    text = ocr_text.replace("\u00A0", " ")  # nbsp
    totals: Dict[str, Optional[float]] = {}

    # Gesamtgewicht (kg)
    totals["total_weight_kg"] = _find_num(r"gesamtgewicht[^0-9]*" + _RX_NUM + r"\s*kg", text)

    # Anzahl der Ausführungen (int)
    aq = _find_num(r"anzahl\s+der\s+ausf(?:[üu]hrungen)?[^0-9]*" + _RX_NUM, text)
    totals["total_quantity"] = float(int(aq)) if aq is not None else None

    # Summe ... m  (try to catch a length total line)
    totals["total_length_m"] = _find_num(r"summe[^0-9]*" + _RX_NUM + r"\s*m\b", text)

    return totals

# ----------------------------
# Canonical mapping (if human CSV is passed)
# ----------------------------
DISPLAY2CANON = {
    "Position":"position",
    "Stück":"quantity",
    "Ø [mm]":"diameter_mm",
    "Einzellänge [m]":"unit_length_m",
    "Gesamtlänge [m]":"total_length_m",
    "Gewicht [kg]":"weight_kg",
}

def _to_canonical(df: pd.DataFrame) -> pd.DataFrame:
    cols = {c.strip(): c for c in df.columns}
    rename = {src: DISPLAY2CANON[src] for src in DISPLAY2CANON if src in cols}
    return df.rename(columns=rename)

# ----------------------------
# Row & table checks
# ----------------------------
def _row_checks(row: Dict[str, Any], idx: int, table_i: int, cfg) -> List[Dict[str, Any]]:
    ws: List[Dict[str, Any]] = []
    allowed = set(_read_cfg_path(cfg, ["validation","allowed_diameters_mm"],
                                 [6,8,10,12,14,16,20,25,28,32,40]))
    len_pct = float(_read_cfg_path(cfg, ["validation","length_tolerance_pct"], 3.0))
    len_abs = float(_read_cfg_path(cfg, ["validation","length_tolerance_abs_m"], 0.10))
    wt_pct  = float(_read_cfg_path(cfg, ["validation","weight_tolerance_pct"], 5.0))
    wt_abs  = float(_read_cfg_path(cfg, ["validation","weight_tolerance_abs_kg"], 0.20))

    pos = _to_int(row.get("position"))
    qty = _to_int(row.get("quantity"))
    dia = _to_int(row.get("diameter_mm"))
    L1  = _to_float(row.get("unit_length_m"))
    LT  = _to_float(row.get("total_length_m"))
    Wkg = _to_float(row.get("weight_kg"))

    # required values
    for field, val in (("position",pos),("quantity",qty),("diameter_mm",dia),
                       ("unit_length_m",L1),("total_length_m",LT),("weight_kg",Wkg)):
        if val is None:
            ws.append({"table":table_i,"row":idx+1,"field":field,"message":"Missing or invalid value"})

    # domains
    if qty is not None and qty <= 0:
        ws.append({"table":table_i,"row":idx+1,"field":"quantity","message":"Quantity must be > 0"})

    if dia is not None and dia not in allowed:
        ws.append({"table":table_i,"row":idx+1,"field":"diameter_mm","message":f"Unexpected Ø value {dia} mm"})

    # totals ≈ qty × unit length
    if None not in (qty, L1, LT):
        expected = qty * L1
        tol = max(expected*(len_pct/100.0), len_abs)
        if abs(LT - expected) > tol:
            ws.append({"table":table_i,"row":idx+1,"field":"total_length_m",
                       "message":f"Gesamtlänge mismatch: {LT} vs qty×Einzellänge {expected:.2f} (±{tol:.2f})"})

    # weight ≈ kg_per_m(Ø) × total length
    if None not in (dia, LT, Wkg):
        kgm = _kg_per_m(dia)
        if kgm is not None:
            expected = kgm * LT
            tol = max(expected*(wt_pct/100.0), wt_abs)
            if abs(Wkg - expected) > tol:
                ws.append({"table":table_i,"row":idx+1,"field":"weight_kg",
                           "message":f"Gewicht mismatch: {Wkg} vs expected {expected:.2f} (±{tol:.2f})"})
    return ws

def _table_checks(df: pd.DataFrame, table_i: int) -> List[Dict[str, Any]]:
    ws: List[Dict[str, Any]] = []
    if "position" in df.columns:
        dup = df["position"].astype(str).str.strip()
        dups = dup[dup.duplicated(keep=False)]
        if not dups.empty:
            rows = [i+1 for i in dups.index.tolist()]
            ws.append({"table": table_i, "message": f"Duplicate Position values at rows {rows}"})
    return ws

def _header_checks(header: Dict[str, Any], cfg) -> List[Dict[str, Any]]:
    ws: List[Dict[str, Any]] = []
    req = set(_read_cfg_path(cfg, ["validation","required_header_fields"], ["PROJECT","DRAWING_NO","DATE"]))
    for k in req:
        if not header or not str(header.get(k, "")).strip():
            ws.append({"header_warning": f"Missing {k} in header"})
    # DATE plausibility
    dv = header.get("DATE")
    if dv and not re.search(r"\b(\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2}|\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})\b", str(dv)):
        ws.append({"header_warning": f"DATE value looks unusual: {dv}"})
    return ws

# ----------------------------
# Optional JSON Schema
# ----------------------------
def _schema_validator() -> Optional[Any]:
    schema_path = Path("table_schema.json")
    if Draft7Validator is None or not schema_path.exists():
        return None
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        return Draft7Validator(schema)
    except Exception:
        return None

# ----------------------------
# Public API
# ----------------------------
def run_validations(csv_paths: List[str], header_data: Dict[str, Any], config=None) -> List[Dict[str, Any]]:
    warnings: List[Dict[str, Any]] = []

    # header checks
    warnings.extend(_header_checks(header_data or {}, config))

    # optional schema
    validator = _schema_validator()

    # auto-detect base for OCR totals
    base = _infer_base_from_csv(csv_paths[0]) if csv_paths else None
    ocr_text = _load_full_text_json(base) if base else None
    totals = _extract_totals_from_ocr(ocr_text or "") if ocr_text else {}

    sum_qty = 0
    sum_len = 0.0
    sum_wgt = 0.0

    for i, p in enumerate(csv_paths or []):
        df = _load_csv(p)
        if df.empty:
            warnings.append({"table": i, "message": "Empty table CSV"})
            continue

        # map to canonical if a human CSV sneaks in
        df = _to_canonical(df)

        # ensure string dtypes; parse per cell later
        for c in ("position","quantity","diameter_mm","unit_length_m","total_length_m","weight_kg"):
            if c in df.columns:
                df[c] = df[c].astype(str).fillna("")

        # JSON Schema (optional) — after coercion to float/int in a temp view
        if validator is not None:
            temp = df.copy()
            def _coerce_col(col, fn): 
                if col in temp: temp[col] = temp[col].map(fn)
            _coerce_col("position", _to_int)
            _coerce_col("quantity", _to_int)
            _coerce_col("diameter_mm", _to_float)
            _coerce_col("unit_length_m", _to_float)
            _coerce_col("total_length_m", _to_float)
            _coerce_col("weight_kg", _to_float)
            for r_i, r in temp.iterrows():
                for err in validator.iter_errors(r.to_dict()):
                    warnings.append({
                        "table": i, "row": r_i+1,
                        "field": list(err.path)[0] if err.path else None,
                        "message": err.message
                    })

        # row + table checks
        for r_i, r in df.iterrows():
            warnings.extend(_row_checks(r.to_dict(), r_i, i, config))
            # accumulate totals (skip None)
            q = _to_int(r.get("quantity")); sum_qty += q or 0
            L = _to_float(r.get("total_length_m")); sum_len += L or 0.0
            w = _to_float(r.get("weight_kg")); sum_wgt += w or 0.0
        warnings.extend(_table_checks(df, i))

    # compare OCR totals if we found any (tolerant)
    if totals:
        # quantity
        if totals.get("total_quantity") is not None and sum_qty:
            if abs(sum_qty - totals["total_quantity"]) > max(1, 0.01*sum_qty):
                warnings.append({"message": f"Anzahl mismatch: table Σ={sum_qty} vs OCR {totals['total_quantity']}"})
        # length (m)
        if totals.get("total_length_m") is not None and sum_len:
            tol = max(0.03*sum_len, 0.10)
            if abs(sum_len - totals["total_length_m"]) > tol:
                warnings.append({"message": f"Summe Länge mismatch: table Σ={sum_len:.2f} m vs OCR {totals['total_length_m']:.2f} m (±{tol:.2f})"})
        # weight (kg)
        if totals.get("total_weight_kg") is not None and sum_wgt:
            tol = max(0.05*sum_wgt, 0.2)
            if abs(sum_wgt - totals["total_weight_kg"]) > tol:
                warnings.append({"message": f"Gesamtgewicht mismatch: table Σ={sum_wgt:.2f} kg vs OCR {totals['total_weight_kg']:.2f} kg (±{tol:.2f})"})

    return warnings
