# grid_utils.py
'''
import cv2
import numpy as np


def detect_table_cells(image):
    """Detects horizontal and vertical lines to infer table cell structure"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blur, 50, 150, apertureSize=3)

    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)
    grid = np.copy(image)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(grid, (x1, y1), (x2, y2), (0, 255, 0), 1)
    return grid, lines
    '''
 
# core/grid_utils.py
# Utilities for grid detection, robust row grouping, column binning from header,
# and safe helpers used by the OCR table parser.

from __future__ import annotations
import cv2
import numpy as np
import pandas as pd
from typing import List, Tuple, Optional


def detect_table_cells(image):
    """
    (Optional/Debug) Detect horizontal/vertical lines to visualize the table grid.
    Useful to sanity-check YOLO crops or OCR pre-processing.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blur, 50, 150, apertureSize=3)

    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)
    grid = np.copy(image)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(grid, (x1, y1), (x2, y2), (0, 255, 0), 1)
    return grid, lines


# ----------------------------
# Robust row grouping helpers
# ----------------------------

def dynamic_row_tolerance(df: pd.DataFrame, fallback: int = 15) -> int:
    """
    Compute a tolerance for grouping tokens into rows from OCR geometry.
    Uses ~60% of median token height, clamped by a fallback minimum.
    """
    if df is None or df.empty or 'height' not in df:
        return fallback
    try:
        med = int(np.median(df['height'].dropna()))
    except Exception:
        med = fallback
    return max(fallback, int(0.6 * (med if med > 0 else fallback)))


def is_header_like_row(tokens: List[str]) -> bool:
    """
    Heuristic to skip header rows when parsing data.
    Targets CISOL/Stahliste patterns.
    """
    import re
    joined = " ".join(tokens).lower()
    return bool(re.search(r"pos|stück|stuck|stueck|einzell(ä|a)nge|gesamtl(ä|a)nge|gewicht|ø|\[", joined))


# ----------------------------
# Column binning from header
# ----------------------------

def header_bins_from_tokens(header_df: pd.DataFrame, col_tolerance: int = 10) -> Optional[List[Tuple[int, int]]]:
    """
    Build x-interval bins from header token geometry to 'snap' subsequent tokens into columns.
    Expects columns: left, width (integers).
    """
    if header_df is None or header_df.empty:
        return None

    df = header_df.sort_values("left").copy()
    bins: List[List[int]] = []
    last_right = None

    for _, r in df.iterrows():
        left = int(r["left"])
        right = int(r["left"] + r["width"])
        if last_right is not None and left - last_right < col_tolerance:
            # Extend the previous bin if the gap is small (header text broken into sub-tokens)
            bins[-1][0] = min(bins[-1][0], left)
            bins[-1][1] = max(bins[-1][1], right)
        else:
            bins.append([left, right])
        last_right = right

    return [(b[0], b[1]) for b in bins]


def snap_to_bins(df: pd.DataFrame, bins: List[Tuple[int, int]]) -> List[Optional[int]]:
    """
    Assign each token to the nearest column bin by x-center.
    Returns a list of column indices (same order as df).
    """
    if not bins or df is None or df.empty:
        return [None] * (0 if df is None else len(df))

    centers = df["left"] + (df["width"] / 2.0)
    bin_centers = [(b[0] + b[1]) / 2.0 for b in bins]
    assigned: List[Optional[int]] = []
    for c in centers:
        dists = [abs(float(c) - float(bc)) for bc in bin_centers]
        idx = int(np.argmin(dists)) if len(dists) else None
        assigned.append(idx)
    return assigned


# ----------------------------
# Helpful band restriction & header reduction
# ----------------------------

def restrict_to_table_band(df_like: pd.DataFrame, bins: List[Tuple[int, int]], pad: int = 6) -> pd.DataFrame:
    """
    Keep only tokens whose x-center lies within the min/max of the header bins (±pad).
    This prevents legends/titles from being snapped to columns.
    """
    if df_like is None or df_like.empty or not bins:
        return df_like
    x_min = min(b[0] for b in bins) - int(pad)
    x_max = max(b[1] for b in bins) + int(pad)
    xc = df_like["left"] + (df_like["width"] / 2.0)
    mask = (xc >= x_min) & (xc <= x_max)
    return df_like[mask].copy()


def _merge_header_tokens(tokens: List[str]) -> str:
    """
    Merge header tokens with special handling for 'Einzel-/Gesamt- Länge' and Ø detection.
    """
    import re
    t = [s.strip() for s in tokens if s and str(s).strip()]
    joined = " ".join(t)

    # Fix common two-line headers
    if ("Einzel-" in joined and "Länge" in joined) or re.search(r"einzel\s*-\s*l(ä|a)nge", joined, re.I):
        joined = "Einzellänge [m]" if "[m]" in joined or "m]" in joined else "Einzellänge"
    if ("Gesamt-" in joined and "Länge" in joined) or re.search(r"gesamt\s*-\s*l(ä|a)nge", joined, re.I):
        joined = "Gesamtlänge [m]" if "[m]" in joined or "m]" in joined else "Gesamtlänge"

    # Ø column detection
    if re.search(r"(ø|@|durchmesser|\[mm\])", joined, re.I):
        joined = "Ø [mm]"

    return joined.strip()


def reduce_header_from_bins(header_df: pd.DataFrame, bins: List[Tuple[int, int]]) -> List[str]:
    """
    Build one label per bin by concatenating header tokens that fall into that bin.
    """
    if header_df is None or header_df.empty or not bins:
        return []

    labels: List[str] = []
    # Precompute token centers
    centers = header_df["left"] + (header_df["width"] / 2.0)
    toks = header_df.assign(_xc=centers)

    for (l, r) in bins:
        in_bin = toks[(toks._xc >= l) & (toks._xc <= r)].sort_values(["top", "left"])
        words = [str(x).strip() for x in in_bin["text"].tolist() if str(x).strip()]
        label = _merge_header_tokens(words) if words else ""
        labels.append(label if label else "")

    # Remove fully empty trailing labels (rare)
    while labels and not labels[-1]:
        labels.pop()

    return labels
