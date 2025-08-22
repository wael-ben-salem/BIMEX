
# core/extractor.py — YOLO → crop → OCR → DataFrame → CSV (display & canonical for validation)

from __future__ import annotations
import os
import json
import unicodedata
from pathlib import Path
from typing import Dict, List

import cv2
import numpy as np
import pandas as pd
from ultralytics import YOLO
import pytesseract

from .ocr_utils import (
    extract_table_ocr,
    extract_header_info,
    build_tess_config,
    _read_cfg_path
)
from .grid_utils import (
    detect_table_cells,
)
from .validation import run_validations
from .config import Config


def _to_outputs_url(p: str | Path) -> str:
    name = Path(p).name
    return f"/outputs/{name}"


def _fold(s: str) -> str:
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower().replace(" ", "")


class SmartTableExtractor:
    def __init__(
        self,
        yolo_model_path: str,
        output_dir: str,
        config: Config,
        translate_headers: bool = False,
        validate_schema: bool = False,
        debug: bool = False
    ):
        self.model = YOLO(yolo_model_path)
        self.output_dir = Path(output_dir)
        self.config = config
        self.translate = translate_headers
        self.validate = validate_schema
        self.debug = debug
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ----------------------------
    # Post-processing for cleaner CSVs
    # ----------------------------
    def postprocess_table(self, df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return df.copy() if df is not None else df

        out = df.copy()

        # Normalize strings, strip junk tokens
        out.replace({'—': np.nan, '―': np.nan, '': np.nan, ' ': np.nan}, inplace=True)
        out = out.replace(r"^[^\w\s]+$", np.nan, regex=True)  # remove rows that are only symbols like "="
        out.infer_objects(copy=False)
        out.dropna(how='all', inplace=True)

        # Trim + Ø normalization + decimal fix
        for c in out.columns:
            if out[c].dtype == object:
                out[c] = (out[c].astype(str)
                          .str.strip()
                          .str.replace("@", "Ø", regex=False))

        # Remove summary/total lines that bleed into the table
        def _row_text(r): return " ".join(str(v) for v in r.dropna().tolist()).lower()
        txt = out.apply(_row_text, axis=1)
        summary_pat = r"\b(summe|gesamtgewicht|anzahl der ausf|anzahl der ausfüh|ausführungen)\b"
        out = out[~txt.str.contains(summary_pat, regex=True)]

        # Keep rows that look like real data (at least 2 numeric across Position/Stück/Ø if present)
        import re
        def _numlike(x): return bool(re.fullmatch(r"\d{1,4}", str(x or "").strip()))
        core = [c for c in ["Position", "Stück", "Ø [mm]"] if c in out.columns]
        if core:
            mask = out.apply(lambda r: sum(_numlike(r.get(c)) for c in core) >= 2, axis=1)
            out = out[mask]

        # Remove tiny noise rows (e.g., stray "S", "N" in Biegeform)
        if "Biegeform" in out.columns:
            def _is_noise_biege(r):
                vals = [str(v).strip() for v in r.dropna().tolist()]
                return len(vals) <= 2 and all(len(v) <= 2 for v in vals)
            out = out[~out.apply(_is_noise_biege, axis=1)]

        out.replace('', np.nan, inplace=True)
        out.dropna(how='all', inplace=True)
        return out

    # ----------------------------
    # Main
    # ----------------------------
    def process(self, image_path: str) -> Dict:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")

        name = Path(image_path).stem
        result: Dict = {
            "image": image_path,
            "original_image": None,
            "header_json": None,
            "table_csvs": [],
            "warnings": [],
            "full_text_json": None,
            "tables": [],
            "table_crop_image": None,
        }

        # Save page image for UI/PDF
        page_img_path = self.output_dir / f"{name}.png"
        try:
            cv2.imwrite(str(page_img_path), image)
            result["original_image"] = _to_outputs_url(page_img_path)
        except Exception:
            pass

        # ---- Header
        header_info = extract_header_info(image, self.config)
        header_path = self.output_dir / f"{name}_header.json"
        with open(header_path, "w", encoding="utf-8") as f:
            json.dump(header_info, f, indent=2, ensure_ascii=False)
        result["header_json"] = _to_outputs_url(header_path)

        # ---- Full OCR dump (debug/audit)
        lang = _read_cfg_path(self.config, ["ocr", "language"], getattr(self.config, "language", "eng+deu"))
        oem = _read_cfg_path(self.config, ["ocr", "oem"], getattr(self.config, "oem", 3))
        psm = _read_cfg_path(self.config, ["ocr", "psm"], getattr(self.config, "psm", 6))
        tessdata_prefix = _read_cfg_path(self.config, ["ocr", "tessdata_prefix"], getattr(self.config, "tessdata_prefix", None))
        blacklist = _read_cfg_path(self.config, ["ocr", "char_blacklist"], "")
        preserve_spaces = _read_cfg_path(self.config, ["ocr", "preserve_interword_spaces"], 1)

        full_cfg = build_tess_config(
            oem=oem, psm=psm, blacklist=blacklist,
            preserve_interword_spaces=preserve_spaces,
            tessdata_prefix=tessdata_prefix
        )
        full_ocr = pytesseract.image_to_data(image, lang=lang, config=full_cfg,
                                             output_type=pytesseract.Output.DICT)
        ocr_blocks: List[Dict] = []
        n = len(full_ocr.get("text", []))
        for i in range(n):
            txt = (full_ocr["text"][i] or "").strip()
            if txt:
                try:
                    conf_val = float(full_ocr["conf"][i])
                except Exception:
                    conf_val = -1.0
                ocr_blocks.append({
                    "text": txt,
                    "left": int(full_ocr["left"][i]),
                    "top": int(full_ocr["top"][i]),
                    "width": int(full_ocr["width"][i]),
                    "height": int(full_ocr["height"][i]),
                    "conf": conf_val,
                })
        full_text_path = self.output_dir / f"{name}_full_text.json"
        with open(full_text_path, "w", encoding="utf-8") as f:
            json.dump(ocr_blocks, f, indent=2, ensure_ascii=False)
        result["full_text_json"] = _to_outputs_url(full_text_path)

        # ---- YOLO detection
        det = self.model(image_path)[0]
        boxes = det.boxes.xyxy.cpu().numpy() if det and det.boxes is not None else np.zeros((0, 4))
        if boxes.shape[0] > 0:
            idx = np.lexsort((boxes[:, 0], boxes[:, 1]))  # sort by y then x
            boxes = boxes[idx]

        validation_csvs: List[str] = []

        # ---- For each detected table
        for i, (x1, y1, x2, y2) in enumerate(boxes):
            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            if (x2 - x1) < 20 or (y2 - y1) < 20:
                continue

            crop = image[y1:y2, x1:x2]
            table_img_path = self.output_dir / f"{name}_table_{i}.png"
            cv2.imwrite(str(table_img_path), crop)

            df = extract_table_ocr(crop, self.config, translate=self.translate, debug=self.debug)
            df = self.postprocess_table(df)

            if df is not None and not df.empty:
                # DISPLAY CSV (what the user sees — German headers, your order)
                csv_path = self.output_dir / f"{name}_table_{i}.csv"
                df.to_csv(csv_path, index=False, encoding="utf-8-sig")

                result["table_csvs"].append(_to_outputs_url(csv_path))
                result["tables"].append({
                    "index": i,
                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                    "shape": [int(df.shape[0]), int(df.shape[1])],
                    "image": _to_outputs_url(table_img_path),
                })
                if i == 0:
                    result["table_crop_image"] = _to_outputs_url(table_img_path)

                # ----- CANONICAL CSV (for validator)
                disp2canon = _read_cfg_path(self.config, ["headers", "display_to_canonical"], {}) or {}

                # fold-insensitive rename
                folded_map = {_fold(k): v for k, v in disp2canon.items()}
                rename_map = {}
                for c in df.columns:
                    fc = _fold(str(c))
                    if fc in folded_map:
                        rename_map[c] = folded_map[fc]

                df_val = df.rename(columns=rename_map).copy()
                validator_cols = ["position", "quantity", "diameter_mm", "unit_length_m", "total_length_m", "weight_kg"]
                keep = [c for c in validator_cols if c in df_val.columns]
                if keep:
                    df_val = df_val[keep]

                val_csv_path = self.output_dir / f"{name}_table_{i}_val.csv"
                df_val.to_csv(val_csv_path, index=False, encoding="utf-8-sig")
                validation_csvs.append(str(val_csv_path))
            else:
                if self.debug:
                    csv_path = self.output_dir / f"{name}_table_{i}_EMPTY.csv"
                    pd.DataFrame().to_csv(csv_path, index=False)
                    result["table_csvs"].append(_to_outputs_url(csv_path))
                    result["tables"].append({
                        "index": i,
                        "bbox": [int(x1), int(y1), int(x2), int(y2)],
                        "shape": [0, 0],
                        "image": _to_outputs_url(table_img_path),
                    })
                    if i == 0:
                        result["table_crop_image"] = _to_outputs_url(table_img_path)

        # ---- Validation (prefer canonical CSVs)
        if self.validate and (validation_csvs or result.get("table_csvs")):
            csvs = validation_csvs if validation_csvs else result["table_csvs"]
            # Read header info file back (it's already JSON-serializable dict)
            try:
                with open(header_path, "r", encoding="utf-8") as f:
                    header_for_val = json.load(f)
            except Exception:
                header_for_val = header_info
            warnings = run_validations(csvs, header_for_val, self.config)
            warn_path = self.output_dir / f"{name}_warnings.json"
            with open(warn_path, "w", encoding="utf-8") as f:
                json.dump(warnings, f, indent=2, ensure_ascii=False)
            result["warnings"] = warnings

        return result
