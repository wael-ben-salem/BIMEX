from app.processors.element_detector import ElementDetector
from app.processors.symbol_detector import SymbolDetector

def detect_symbols_and_elements(file_path: str):
    import time
    start_time = time.time()

    # Detect symbols
    symbol_detector = SymbolDetector()
    symbols = symbol_detector.detect_symbols(file_path)

    # Detect elements
    element_detector = ElementDetector()
    elements, _ = element_detector.detect_elements(file_path)

    total_processing_time = time.time() - start_time
    return symbols, elements, total_processing_time
