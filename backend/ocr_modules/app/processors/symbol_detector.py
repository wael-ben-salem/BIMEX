import time
import cv2
import numpy as np
from typing import List
from app.models.ocr_models import DetectedSymbolModel

class SymbolDetector:
    def __init__(self, min_area: float = 50):
        self.min_area = min_area  # filter tiny contours / noise

    def detect_symbols_from_image(self, image: np.ndarray) -> List[DetectedSymbolModel]:
        """
        Detect BIM symbols in a blueprint image.
        Returns list of DetectedSymbolModel.
        """
        symbols = []

        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # Apply adaptive thresholding to capture blueprint lines and symbols
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                       cv2.THRESH_BINARY_INV, 15, 5)

        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_area:
                continue  # skip tiny noise

            x, y, w, h = cv2.boundingRect(contour)

            # Classify BIM symbol type using aspect ratio and size heuristics
            symbol_type = self.classify_bim_symbol(w, h)

            symbols.append(
                DetectedSymbolModel(
                    name=symbol_type,
                    bbox=[x, y, x + w, y + h],
                    confidence=100  # placeholder for ML model confidence
                )
            )

        return symbols

    def classify_bim_symbol(self, width: int, height: int) -> str:
        """
        Classify symbol based on size/aspect ratio.
        These heuristics can be replaced with ML template matching or trained model.
        """
        aspect_ratio = width / height if height > 0 else 0

        # Example BIM blueprint heuristics
        if 0.8 <= aspect_ratio <= 1.2 and max(width, height) < 50:
            return "column_symbol"
        elif aspect_ratio > 2.5 and width > 50:
            return "beam_symbol"
        elif aspect_ratio < 0.5 and height > 50:
            return "door_symbol"
        elif 1.5 <= aspect_ratio <= 2.5 and max(width, height) > 30:
            return "window_symbol"
        else:
            return "generic_fixture_symbol"

    def detect_symbols(self, file_path: str) -> List[DetectedSymbolModel]:
        """
        Main function for vision_engine.py
        """
        start_time = time.time()

        image = cv2.imread(file_path)
        if image is None:
            raise FileNotFoundError(f"Could not read image at {file_path}")

        symbols = self.detect_symbols_from_image(image)
        processing_time = time.time() - start_time
        # optionally return processing_time if needed
        return symbols
