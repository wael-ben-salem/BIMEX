import os
from app.core.vision_engine import detect_symbols_and_elements

# Replace this with your file_id
file_id = "c1841bee-3715-40f5-868a-82bcdbcbefd8"

# Construct the path to the uploaded image
upload_folder = os.path.join("data", "uploads", file_id)
file_path = None

# Find the file starting with "original."
for fname in os.listdir(upload_folder):
    if fname.startswith("original."):
        file_path = os.path.join(upload_folder, fname)
        break

if not file_path:
    raise FileNotFoundError(f"No file starting with 'original.' found in {upload_folder}")

# Run vision detection
symbols, elements, processing_time = detect_symbols_and_elements(file_path)

# Print results
print(f"Processing time: {processing_time:.2f}s\n")

print("Detected Symbols:")
for s in symbols:
    print(f"- {s.name}, bbox: {s.bbox}, confidence: {s.confidence}")

print("\nDetected Elements:")
for e in elements:
    print(f"- {e.element_type}, bbox: {e.bbox}, confidence: {e.confidence}")
