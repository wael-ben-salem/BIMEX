import re
import spacy
from typing import Dict, Any, List
import pandas as pd

# Load German and English pipelines (fallback to blank if not installed)
try:
    nlp_de = spacy.load("de_core_news_sm")
except OSError:
    nlp_de = spacy.blank("de")

try:
    nlp_en = spacy.load("en_core_web_sm")
except OSError:
    nlp_en = spacy.blank("en")

class NLPValidator:
    """
    Extracts key entities from header text and validates extracted tables and headers.
    """
    def __init__(self, language: str = "de"):
        # Choose spaCy pipeline based on language
        self.nlp = nlp_de if language.lower().startswith("de") else nlp_en
        # Regex patterns for fallbacks
        self.date_re = re.compile(r"\d{1,2}[./]\d{1,2}[./]\d{2,4}")
        self.numeric_re = re.compile(r"^-?\d+(?:[.,]\d+)?$")

    def extract_header_entities(self, raw_header_text: str) -> Dict[str, str]:
        """
        Use spaCy NER (and regex fallback) to pull out Date, Bearbeiter, and Project.
        """
        doc = self.nlp(raw_header_text)
        entities: Dict[str, str] = {}
        for ent in doc.ents:
            if ent.label_ == "DATE":
                entities.setdefault("Date", ent.text)
            elif ent.label_ == "PERSON":
                entities.setdefault("Bearbeiter", ent.text)
            elif ent.label_ in ("ORG", "PRODUCT", "GPE", "LOC"):
                # first org/product/gpe as Project
                entities.setdefault("Projekt", ent.text)
        # Regex fallback for date
        if "Date" not in entities:
            m = self.date_re.search(raw_header_text)
            if m:
                entities["Date"] = m.group()
        return entities

    def validate(self,
                 header: Dict[str, Any],
                 tables: List[pd.DataFrame]
    ) -> List[str]:
        """
        Run generic checks: missing header fields, non-numeric entries, missing values.
        """
        warnings: List[str] = []
        # 1) Header completeness
        for field in ("Projekt", "Bearbeiter", "Date"):
            if not header.get(field):
                warnings.append(f"Missing header field: {field}")

        # 2) Table validation
        for idx, df in enumerate(tables):
            # Missing values
            if df.isnull().any().any():
                warnings.append(f"Table {idx}: missing values detected")
            # Non-numeric where numeric expected
            for col in df.columns:
                # heuristics: if name contains common unit or numeric hint
                key = col.lower()
                if any(tok in key for tok in ["stück", "anzahl", "qty", "length", "länge", "gew", "kg", "mm"]):
                    bad = df[~df[col].astype(str).str.match(self.numeric_re)]
                    if not bad.empty:
                        warnings.append(f"Table {idx}: non-numeric entries in '{col}'")
        return warnings
