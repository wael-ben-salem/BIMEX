# config.py
'''
# Old Script 
import yaml
from dataclasses import dataclass
from typing import Optional
import os 

@dataclass
class Config:
    tessdata_prefix: str = r"C:\\Program Files\\Tesseract-OCR\\tessdata"
    tesseract_path: str = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    language: str = "deu"
    oem: int = 3
    psm: int = 6
    confidence_threshold: int = 30
    row_tolerance: int = 15
    header_crop_ratio: float = 0.15


def load_config(path: Optional[str] = None) -> Config:
    if path and path.endswith(".yaml") and os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            raw = yaml.safe_load(f)
        return Config(**raw)
    return Config()


CANONICAL_COLUMNS = [
    "position",
    "quantity",
    "diameter_mm",
    "length_m",
    "total_length_m",
    "weight_kg"
]

COLUMN_MAPPING = {
    "position":     ["position","pos.","pos","nr.:","nr","nr.","no.pcs"],
    "quantity":     ["stück","stk.","stck","st.","anzahl","anz.","anz","no.pcs"],
    "diameter_mm":  ["d","d(mm)","durchmesser","d8","d10","d12","durchmesser", "ø", "ø [mm]"],
    "length_m":     ["einzellänge","einzel-","schnittlänge","länge"],
    "total_length_m":["gesamtlänge","ges.länge","ges.l","gesamt-"],
    "weight_kg":    ["gewicht","gew.","gewich:","gewicht(kg)","masse"]
}

def canonicalize_columns(df):
    from difflib import get_close_matches
    new_cols = {}
    for col in df.columns:
        key = str(col).strip().lower()
        mapped = None
        for canon, syns in COLUMN_MAPPING.items():
            if key in syns:
                mapped = canon
                break
        if not mapped:
            all_syns = [s for syns in COLUMN_MAPPING.values() for s in syns]
            close = get_close_matches(key, all_syns, n=1, cutoff=0.8)
            if close:
                for canon, syns in COLUMN_MAPPING.items():
                    if close[0] in syns:
                        mapped = canon
                        break
        if mapped:
            new_cols[col] = mapped
    return df.rename(columns=new_cols, inplace=False)
'''
# backend/core/config.py
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import yaml
import os

@dataclass
class Config:
    raw: Dict[str, Any] = field(default_factory=dict)

    # dict-like access
    def __getitem__(self, k): return self.raw.get(k)
    def get(self, k, default=None): return self.raw.get(k, default)

    # attribute-like access (optional)
    def __getattr__(self, k: str) -> Optional[Any]:
        try:
            return self.raw[k]
        except KeyError:
            raise AttributeError(k)

def load_config(path: str = "configs/default.yaml") -> Config:
    if not os.path.exists(path):
        # Graceful fallback: return empty config and let code defaults handle it
        return Config(raw={})
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return Config(raw=data)


# (Optional legacy helper kept so old imports don’t break)
from difflib import get_close_matches

CANONICAL_COLUMNS = [
    "position",
    "quantity",
    "diameter_mm",
    "unit_length_m",    
    "total_length_m",
    "weight_kg"
]

COLUMN_MAPPING = {
    "position":     ["position","pos.","pos","nr.:","nr","nr.","no.pcs","#"],
    "quantity":     ["stück","stk.","stck","st.","anzahl","anz.","anz","no.pcs","stuck","stük"],
    "diameter_mm":  ["durchmesser","ø","ø [mm]","d(mm)","d8","d10","d12","d"],
    "unit_length_m":["einzellänge","einzel-","schnittlänge","länge","einzellange","einzellange [m]"],
    "total_length_m":["gesamtlänge","ges.länge","ges.l","gesamt-","gesamtlange"],
    "weight_kg":    ["gewicht","gew.","gewicht(kg)","masse","gewich:"]
}

def canonicalize_columns(df):
    new_cols = {}
    for col in df.columns:
        key = str(col).strip().lower()
        mapped = None
        # exact map
        for canon, syns in COLUMN_MAPPING.items():
            if key in syns:
                mapped = canon
                break
        # fuzzy map
        if not mapped:
            all_syns = [s for syns in COLUMN_MAPPING.values() for s in syns]
            close = get_close_matches(key, all_syns, n=1, cutoff=0.8)
            if close:
                for canon, syns in COLUMN_MAPPING.items():
                    if close[0] in syns:
                        mapped = canon
                        break
        if mapped:
            new_cols[col] = mapped
    return df.rename(columns=new_cols, inplace=False)

