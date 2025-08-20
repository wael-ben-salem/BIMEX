import logging
import re
import json
from typing import List, Optional
import pytesseract
from PIL import Image
from app.models.ocr_models import OCRTextItem
from groq import Groq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextExtractor:
    def __init__(self, use_llm=True, groq_api_key=None, max_tokens=1500, languages: Optional[List[str]] = None):
        self.use_llm = use_llm
        self.max_tokens = max_tokens
        self.languages = languages
        self.groq_client = Groq(api_key=groq_api_key) if groq_api_key else None

    def extract_text(self, image_path: str, languages: Optional[List[str]] = None) -> List[OCRTextItem]:
        langs = ",".join(languages) if languages else (",".join(self.languages) if self.languages else "eng")
        logger.info(f"Processing image: {image_path} with languages: {langs}")

        # 1️⃣ OCR extraction
        img = Image.open(image_path)
        data = pytesseract.image_to_data(img, lang=langs, output_type=pytesseract.Output.DICT)

        ocr_words = []
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            if not text:
                continue
            conf = float(data['conf'][i]) if data['conf'][i] != -1 else 1.0
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            ocr_words.append({
                "text": text,
                "confidence": conf,
                "x": x,
                "y": y,
                "width": w,
                "height": h
            })

        if not self.use_llm or not self.groq_client:
            return [OCRTextItem(**w, type="label") for w in ocr_words]

        # 2️⃣ Merge words by approximate lines
        lines = {}
        for w in ocr_words:
            line_key = round(w['y'] / 10)
            lines.setdefault(line_key, []).append(w)

        ocr_phrases = [" ".join([w['text'] for w in words]) for words in lines.values()]
        full_text = "\n".join(ocr_phrases)

        # 3️⃣ Strong LLM prompt asking for top 40 meaningful groups
        prompt = f"""
You are an expert in construction blueprints and OCR text analysis.

Task:
1. From the entire OCR text below, identify the  most meaningful semantic units.
   - Each unit should consist of **2 or more words** whenever possible.
   - Only include units with **clear meaning** relevant to construction, architecture, or structural details.
2. Classify each unit into one of these types: label, dimension, location, beam_type, material, other.
3. Ignore line breaks and OCR splits — merge words logically based on meaning and context.
4. Avoid trivial single words unless they form a complete semantic unit.

Return ONLY a valid JSON array like:
[{{"text": "group of words", "type": "..." }}]

OCR text:
{full_text}
"""

        # 4️⃣ Send to Groq LLaMA
        try:
            logger.info("Sending text to Groq LLaMA for classification...")
            chat_completion = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                stream=False
            )
            llm_output = chat_completion.choices[0].message.content
            logger.info("LLM output received")
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            llm_output = ""

        # 5️⃣ Parse JSON output robustly
        classified_texts = []
        try:
            match = re.search(r'\[.*\]', llm_output, re.DOTALL)
            if match:
                json_str = match.group(0)
                json_str = re.sub(r",\s*}", "}", json_str)
                json_str = re.sub(r",\s*]", "]", json_str)
                classified_texts = json.loads(json_str)
                # Keep only meaningful multi-word units
                classified_texts = [c for c in classified_texts if len(c['text'].split()) > 1 or c['type'] != "label"]
                # Take only top 40
                classified_texts = classified_texts[:40]
            else:
                raise ValueError("No JSON found")
        except Exception as e:
            logger.warning(f"LLM output parsing failed: {e}. Using OCR phrases as fallback.")
            classified_texts = [{"text": phrase, "type": "other"} for phrase in ocr_phrases[:40]]

        # 6️⃣ Merge LLM classification with OCR coordinates
        result_items = []
        for classified in classified_texts:
            phrase = classified['text']
            typ = classified.get('type', 'other')

            # Partial match OCR words in phrase
            words_in_phrase = [w for w in ocr_words if re.search(r'\b{}\b'.format(re.escape(w['text'])), phrase, flags=re.I)]
            if not words_in_phrase:
                continue

            x_min = min(w['x'] for w in words_in_phrase)
            y_min = min(w['y'] for w in words_in_phrase)
            x_max = max(w['x'] + w['width'] for w in words_in_phrase)
            y_max = max(w['y'] + w['height'] for w in words_in_phrase)
            width = x_max - x_min
            height = y_max - y_min
            confidence = sum(w['confidence'] for w in words_in_phrase) / len(words_in_phrase)

            result_items.append(OCRTextItem(
                text=phrase,
                x=x_min,
                y=y_min,
                width=width,
                height=height,
                confidence=confidence,
                type=typ
            ))

        logger.info(f"Processed {len(result_items)} OCR items with LLM classification")
        return result_items
