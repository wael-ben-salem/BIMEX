# core/ocr_utils.py
# OCR configuration, header extraction, and robust table parsing using
# header-driven column bins + safe numeric/Ø normalization.

from __future__ import annotations
import os
import re
import unicodedata
from typing import Dict, List, Tuple, Optional

import cv2
import numpy as np
import pandas as pd
import pytesseract

# Optional: spaCy semantic fallback (kept, but not required)
try:
    import spacy
    nlp = spacy.load("en_core_web_md")
except Exception:
    nlp = None

# pull stable helpers from grid_utils
from .grid_utils import (
    dynamic_row_tolerance,
    header_bins_from_tokens,
    snap_to_bins,
    restrict_to_table_band,
    reduce_header_from_bins,
)


# ----------------------------
# Tesseract config & utilities
# ----------------------------

def build_tess_config(
    oem: int = 3,
    psm: int = 6,
    blacklist: str = "",
    preserve_interword_spaces: int = 1,
    tessdata_prefix: Optional[str] = None,
) -> str:
    if tessdata_prefix:
        os.environ["TESSDATA_PREFIX"] = str(tessdata_prefix).rstrip("\\/")

    parts = [
        f"--oem {oem}",
        f"--psm {psm}",
        f"-c preserve_interword_spaces={preserve_interword_spaces}",
    ]
    # keep blacklist empty to preserve '@' → we'll normalize to Ø later
    if blacklist:
        parts.append(f"-c tessedit_char_blacklist={blacklist}")
    return " ".join(parts)


def _read_cfg_path(cfg, path: List[str], default=None):
    cur = cfg
    for key in path:
        if cur is None:
            return default
        if isinstance(cur, dict):
            cur = cur.get(key, None)
        else:
            cur = getattr(cur, key, None)
    return default if cur is None else cur


# ----------------------------
# Normalization & mapping
# ----------------------------

def normalize_text(s: str, symbol_map: Optional[Dict[str, str]] = None,
                   replacements: Optional[List[List[str]]] = None) -> str:
    if not isinstance(s, str):
        s = str(s) if s is not None else ""
    if symbol_map:
        for a, b in symbol_map.items():
            s = s.replace(a, b)
    if replacements:
        for a, b in replacements:
            s = s.replace(a, b)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def ascii_fold_lower(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"\s+", "", s.lower())


def canonicalize_headers(cols: List[str], canonical_map: Optional[List[List[str]]] = None) -> List[str]:
    if not canonical_map:
        return cols
    out = []
    for raw in cols:
        key = ascii_fold_lower(raw)
        mapped = None
        for pattern, name in canonical_map:
            if re.match(pattern, key):
                mapped = name
                break
        out.append(mapped or raw)
    return out


def merge_two_row_header(r1: List[str], r2: List[str]) -> List[str]:
    merged = []
    m = max(len(r1), len(r2))
    for i in range(m):
        a = r1[i].strip() if i < len(r1) else ""
        b = r2[i].strip() if i < len(r2) else ""
        if (a, b) in (("Einzel-", "Länge [m]"), ("Gesamt-", "Länge [m]")):
            merged.append(a.replace("-", "") + " " + b)  # Einzellänge [m], Gesamtlänge [m]
        elif re.search(r"(ø|Ø)|diameter|\[mm\]", a, re.I) or re.search(r"\[mm\]", b, re.I):
            merged.append("Ø [mm]")
        else:
            merged.append((a + " " + b).strip() if (a and b) else (a or b))
    return [c for c in merged if c]


def is_units_row(tokens: List[str]) -> bool:
    joined = " ".join(tokens)
    return bool(re.search(r"\[(?:m|kg|mm)\]", joined, re.I))


def is_title_row(tokens: List[str]) -> bool:
    if not tokens:
        return False
    letters = sum(ch.isalpha() for t in tokens for ch in t)
    digits = sum(ch.isdigit() for t in tokens for ch in t)
    return letters >= 8 and digits <= 2  # lots of text, hardly any numbers


# ----------------------------
# Legacy helpers (compatibility)
# ----------------------------

HEADER_ALIASES = {
    "position": ["pos.", "pos", "position"],
    "diameter_mm": ["durchmesser", "ø", "ø [mm]"],
    "single_length_m": ["einzellänge", "einzel-", "schnittlänge", "länge"],
    "total_length_m": ["gesamtlänge", "ges.länge", "ges.l", "gesamt-", "–gesamtlänge"],
    "weight_kg": ["gewicht", "gew.", "gewich:", "gewicht(kg)", "weight", "masse", "mattengewichte"],
    "quantity": ["stück", "stuck", "stük", "anzahl"],
}
FLAT_MAP = {v.lower(): canon for canon, vs in HEADER_ALIASES.items() for v in vs}


def normalize_column(col: str) -> str:
    text = (col or "").strip().lower()
    best = None
    try:
        import difflib
        best = difflib.get_close_matches(text, FLAT_MAP.keys(), n=1, cutoff=0.8)
    except Exception:
        pass
    if best:
        return FLAT_MAP[best[0]]
    if nlp is not None:
        try:
            doc = nlp(text)
            sims = [(canon, doc.similarity(nlp(canon.replace("_", " ")))) for canon in HEADER_ALIASES.keys()]
            best_sem = max(sims, key=lambda x: x[1]) if sims else (None, 0.0)
            if best_sem[1] > 0.70:
                return best_sem[0]
        except Exception:
            pass
    return text


# ----------------------------
# Header extraction
# ----------------------------

def extract_header_info(image, cfg) -> Dict:
    hdr_ratio = _read_cfg_path(cfg, ["header_crop_ratio"], 0.15)
    lang = _read_cfg_path(cfg, ["ocr", "language"], "eng+deu") or getattr(cfg, "language", "eng+deu")
    oem = _read_cfg_path(cfg, ["ocr", "oem"], getattr(cfg, "oem", 3))
    psm = _read_cfg_path(cfg, ["ocr", "psm"], getattr(cfg, "psm", 6))
    tessdata_prefix = _read_cfg_path(cfg, ["ocr", "tessdata_prefix"], None)
    blacklist = _read_cfg_path(cfg, ["ocr", "char_blacklist"], "")
    preserve_spaces = _read_cfg_path(cfg, ["ocr", "preserve_interword_spaces"], 1)
    key_map = _read_cfg_path(cfg, ["headers", "key_map"], {}) or getattr(cfg, "key_map", {})

    h = int(image.shape[0] * float(hdr_ratio))
    crop = image[:h, :]

    tess_config = build_tess_config(
        oem=oem, psm=psm, blacklist=blacklist,
        preserve_interword_spaces=preserve_spaces,
        tessdata_prefix=tessdata_prefix
    )
    text = pytesseract.image_to_string(crop, lang=lang, config=tess_config)

    header = {}
    for line in text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            header[k.strip()] = v.strip()

    if isinstance(key_map, dict) and key_map:
        mapped = {}
        for k, v in header.items():
            mapped[key_map.get(k, k)] = v
        header = mapped

    return header


# ----------------------------
# Table OCR & parsing (MAIN)
# ----------------------------
 
def extract_table_ocr(image, config, translate: bool = False, debug: bool = False) -> pd.DataFrame:
    import re
    # --- read config
    lang = _read_cfg_path(config, ["ocr", "language"], getattr(config, "language", "eng+deu"))
    oem = _read_cfg_path(config, ["ocr", "oem"], getattr(config, "oem", 3))
    psm = _read_cfg_path(config, ["ocr", "psm"], getattr(config, "psm", 6))
    tessdata_prefix = _read_cfg_path(config, ["ocr", "tessdata_prefix"], getattr(config, "tessdata_prefix", None))
    blacklist = _read_cfg_path(config, ["ocr", "char_blacklist"], "")  # keep empty; we'll fix Ø via symbol_map
    preserve_spaces = _read_cfg_path(config, ["ocr", "preserve_interword_spaces"], 1)
    conf_thr = int(_read_cfg_path(config, ["ocr", "confidence_threshold"], getattr(config, "confidence_threshold", 30)))
    hdr_thr = max(10, conf_thr - 20)

    row_tol_base = int(_read_cfg_path(config, ["table", "row_tolerance"], getattr(config, "row_tolerance", 15)))
    hdr_merge_tol = int(_read_cfg_path(config, ["table", "header_col_merge_tolerance"], 120))
    dyn_row = bool(_read_cfg_path(config, ["table", "dynamic_row_tolerance"], True))
    use_bins = bool(_read_cfg_path(config, ["table", "column_binning_from_header"], True))
    pad = int(_read_cfg_path(config, ["table", "table_band_pad"], 6))

    # normalization (extend with BemaBte→Bemaßte)
    symbol_map = _read_cfg_path(config, ["normalization", "symbol_map"],
                                {"@": "Ø", "O/": "Ø", "0/": "Ø", "o/": "Ø", "Ø/": "Ø"}) or {}
    replacements = (_read_cfg_path(config, ["normalization", "replacements"], []) or []) + [["BemaBte","Bemaßte"]]
    canonical_map = _read_cfg_path(config, ["headers", "canonical_map"], []) or []
    final_order = _read_cfg_path(config, ["headers", "final_display_order"], None)

    tess_config = build_tess_config(
        oem=oem, psm=psm, blacklist=blacklist,
        preserve_interword_spaces=preserve_spaces,
        tessdata_prefix=tessdata_prefix
    )

    # --- light preproc (keep the grid)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (1, 1), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)

    d_raw = pytesseract.image_to_data(thresh, lang=lang, config=tess_config,
                                      output_type=pytesseract.Output.DATAFRAME)
    d_raw["text"] = d_raw["text"].astype(str).map(lambda s: normalize_text(s, symbol_map, replacements))
    d_raw = d_raw[d_raw["text"].str.strip().ne("")]

    d = d_raw[(d_raw.conf.notna()) & (d_raw.conf.astype(float) > conf_thr)].copy()
    d_hdr = d_raw[(d_raw.conf.notna()) & (d_raw.conf.astype(float) > hdr_thr)].copy()
    if d.empty and not d_hdr.empty:
        d = d_hdr.copy()
    if d.empty:
        return pd.DataFrame()

    # --- BODY rows
    row_tol = dynamic_row_tolerance(d, row_tol_base) if dyn_row else row_tol_base
    d = d.sort_values(["top", "left"]).reset_index(drop=True)
    rows_geom = []
    cur, cur_top = [], int(d.iloc[0]["top"])
    for _, tok in d.iterrows():
        ttop = int(tok["top"])
        if abs(ttop - cur_top) <= row_tol:
            cur.append(tok)
        else:
            if cur: rows_geom.append(cur)
            cur, cur_top = [tok], ttop
    if cur: rows_geom.append(cur)

    # --- HEADER bins (primary)
    columns, header_geom, bins = [], pd.DataFrame(), None
    if not d_hdr.empty:
        row_tol_hdr = dynamic_row_tolerance(d_hdr, row_tol_base) if dyn_row else row_tol_base
        d_hdr = d_hdr.sort_values(["top", "left"]).reset_index(drop=True)

        rows_hdr, cur_h, cur_top_h = [], [], int(d_hdr.iloc[0]["top"])
        for _, tok in d_hdr.iterrows():
            ttop = int(tok["top"])
            if abs(ttop - cur_top_h) <= row_tol_hdr:
                cur_h.append(tok)
            else:
                if cur_h: rows_hdr.append(cur_h)
                cur_h, cur_top_h = [tok], ttop
        if cur_h: rows_hdr.append(cur_h)

        header_rows = rows_hdr[:2]
        if header_rows:
            header_geom = pd.concat([pd.DataFrame(r) for r in header_rows], ignore_index=True)

        if use_bins and not header_geom.empty:
            bins = header_bins_from_tokens(header_geom[["left", "width"]].copy(), col_tolerance=hdr_merge_tol)
            # fallback if bins are under-merged (prevents column shift)
            if bins and len(bins) < 4:
                bins = header_bins_from_tokens(header_geom[["left", "width"]].copy(), col_tolerance=max(200, hdr_merge_tol))

    if bins:
        header_geom = restrict_to_table_band(header_geom, bins, pad=pad)
        columns = reduce_header_from_bins(header_geom, bins)
        columns = canonicalize_headers(columns, canonical_map)

    # ====== BODY-DERIVED BIN FALLBACK (robust) ======
    def _numeric_like(s: str) -> bool:
        return bool(re.fullmatch(r"\d+(?:[.,]\d+)?", s or ""))

    need_fallback = (not bins) or (len([c for c in columns if c]) < 5)
    if need_fallback:
        # Collect numeric tokens from body to detect the 6 numeric columns:
        # Position | Stück | Ø | Einzellänge [m] | Gesamtlänge [m] | Gewicht [kg]
        num_df = d[d["text"].apply(_numeric_like)].copy()
        if not num_df.empty:
            num_df["xc"] = num_df["left"] + num_df["width"] / 2.0
            num_df = num_df.sort_values("xc")
            # 1D clustering by gap (no sklearn) → group centers that are closer than 'gap'
            # choose gap from page width / 40 (safe) with clamp
            W = image.shape[1]
            gap = max(40, int(W / 40))
            groups = []
            g = [num_df.iloc[0]]
            for _, r in num_df.iloc[1:].iterrows():
                if (r["xc"] - g[-1]["xc"]) <= gap:
                    g.append(r)
                else:
                    groups.append(pd.DataFrame(g))
                    g = [r]
            if g: groups.append(pd.DataFrame(g))

            # Merge near groups until we have between 5 and 7 (we expect 6 numeric cols)
            def _combine_nearest(gs):
                if len(gs) <= 7: return gs
                merged = []
                i = 0
                while i < len(gs):
                    if i < len(gs)-1:
                        # if successive groups are very close, merge them
                        cx1 = gs[i]["xc"].median(); cx2 = gs[i+1]["xc"].median()
                        if abs(cx2 - cx1) < gap * 0.8:
                            merged.append(pd.concat([gs[i], gs[i+1]], ignore_index=True))
                            i += 2
                            continue
                    merged.append(gs[i]); i += 1
                return merged

            while len(groups) > 7:
                groups = _combine_nearest(groups)

            # Keep the 6 most populated groups (numeric columns)
            groups = sorted(groups, key=lambda df_: (-len(df_), df_["xc"].median()))
            groups = sorted(groups[:6], key=lambda df_: df_["xc"].median())

            # Build bins from groups
            num_bins = []
            for gdf in groups:
                l = int((gdf["left"]).min())
                r = int((gdf["left"] + gdf["width"]).max())
                num_bins.append((l, r))

            # Inject Biegeform bin between Ø and Einzellänge:
            # Expected order: 0:Position, 1:Stück, 2:Ø, 3:Einzellänge, 4:Gesamtlänge, 5:Gewicht
            if len(num_bins) >= 6:
                lØ, rØ = num_bins[2]
                lE, rE = num_bins[3]
                b_left  = rØ + 10
                b_right = lE - 10
                if b_right > b_left:
                    bins = [num_bins[0], num_bins[1], num_bins[2], (b_left, b_right),
                            num_bins[3], num_bins[4], num_bins[5]]
                    # force canonical display headers in this order
                    columns = ["Position", "Stück", "Ø [mm]", "Biegeform", "Einzellänge [m]", "Gesamtlänge [m]", "Gewicht [kg]"]
                else:
                    # if we can't create a Biegeform band, just use numeric columns
                    bins = num_bins
                    columns = ["Position", "Stück", "Ø [mm]", "Einzellänge [m]", "Gesamtlänge [m]", "Gewicht [kg]"]

    # ====== parse rows using bins/columns (no change) ======
    parsed = []
    for r in rows_geom:
        r_sorted = sorted(r, key=lambda z: int(z["left"]))
        row_tokens = [str(x["text"]).strip() for x in r_sorted if str(x["text"]).strip()]
        joined = " ".join(row_tokens).lower()

        # Skip header-like/units/title rows
        if re.search(r"pos|stück|stuck|stueck|einzell(ä|a)nge|gesamtl(ä|a)nge|gewicht|ø|\[", joined):
            continue
        letters = sum(ch.isalpha() for t in row_tokens for ch in t)
        digits  = sum(ch.isdigit() for t in row_tokens for ch in t)
        if letters >= 8 and digits <= 2:
            continue

        if bins and columns:
            r_df = pd.DataFrame(r_sorted)
            # restrict to table band
            x_min = min(b[0] for b in bins) - int(pad)
            x_max = max(b[1] for b in bins) + int(pad)
            xc = r_df["left"] + (r_df["width"] / 2.0)
            r_df = r_df[(xc >= x_min) & (xc <= x_max)]
            # snap to bins
            idxs = snap_to_bins(r_df[["left", "width"]], bins)
            row_dict = {c: "" for c in columns}
            for tok, ci in zip(r_df.to_dict("records"), idxs):
                if ci is None or ci >= len(columns): continue
                col = columns[ci]
                val = str(tok["text"]).strip()
                row_dict[col] = (row_dict[col] + " " + val).strip() if row_dict[col] else val
            if any(v for v in row_dict.values()):
                parsed.append(row_dict)
        else:
            # desperate fallback — linear split
            row_dict = {}
            for i, val in enumerate(row_tokens):
                key = columns[i] if i < len(columns) and columns[i] else f"Column_{i+1}"
                row_dict[key] = val
            if any(v for v in row_dict.values()):
                parsed.append(row_dict)

    df = pd.DataFrame(parsed)

    # Optional translation to canonical names (legacy)
    if translate and not df.empty:
        df.columns = [normalize_column(c) for c in df.columns]
        canonical = ["position", "quantity", "diameter_mm", "unit_length_m", "total_length_m", "weight_kg"]
        known = [c for c in canonical if c in df.columns]
        unknown = [c for c in df.columns if c not in known]
        df = df[known + unknown]

    # Decimal normalization
    for col in df.columns:
        if df[col].dtype == object:
            mask = df[col].str.match(r"^\d+[.,]?\d*$", na=False)
            df.loc[mask, col] = df.loc[mask, col].str.replace(",", ".", regex=False)

    # Recover "Position" if first col is mostly integers
    if not df.empty and "Position" not in df.columns and len(df.columns) > 0:
        first_col = df.columns[0]
        series = df[first_col].astype(str).str.fullmatch(r"\d+")
        if series.mean() >= 0.60:
            df = df.rename(columns={first_col: "Position"})

    # Ensure final display order (when provided)
    if final_order and not translate:
        for col in final_order:
            if col not in df.columns:
                df[col] = ""
        ordered = [c for c in final_order if c in df.columns]
        extras = [c for c in df.columns if c not in final_order]
        if ordered:
            df = df[ordered + extras]

    return df
