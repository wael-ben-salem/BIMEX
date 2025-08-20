import time
from pathlib import Path
import cv2
from PIL import Image
import numpy as np
from typing import List
from app.models.ocr_models import DetectedElementModel

class ElementDetector:
    def __init__(self, min_area: float = 100):
        self.min_area = min_area  # filter tiny contours

    def detect_elements_from_image(self, image: np.ndarray) -> List[DetectedElementModel]:
        """
        Detect structural elements in a single image (numpy array).
        Returns list of DetectedElementModel.
        """
        elements = []

        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # Apply thresholding to get binary image
        _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_area:
                continue  # skip tiny contours

            x, y, w, h = cv2.boundingRect(contour)
            element_type = self.classify_element_by_shape(w, h)

            elements.append(
                DetectedElementModel(
                    element_type=element_type,
                    bbox=[x, y, x + w, y + h],
                    confidence=100  # placeholder, you can add a classifier later
                )
            )

        return elements

    def classify_element_by_shape(self, width: int, height: int) -> str:
        """
        Classify element type based on aspect ratio.
        """
        aspect_ratio = width / height if height > 0 else 0

        if 0.8 <= aspect_ratio <= 1.2:
            return 'column'
        elif aspect_ratio > 3:
            return 'beam'
        elif aspect_ratio < 0.3:
            return 'wall'
        elif 1.5 <= aspect_ratio <= 2.5:
            return 'room'
        else:
            return 'element'

    def detect_elements(self, file_path: str) -> (List[DetectedElementModel], float):
        """
        Main function to call from vision_engine.py.
        Takes image path and returns list of DetectedElementModel + processing_time.
        """
        start_time = time.time()

        # Open image with OpenCV
        image = cv2.imread(file_path)
        if image is None:
            raise FileNotFoundError(f"Could not read image at {file_path}")

        elements = self.detect_elements_from_image(image)
        processing_time = time.time() - start_time

        return elements, processing_time
