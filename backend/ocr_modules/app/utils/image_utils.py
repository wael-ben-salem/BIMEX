# app/utils/image_utils.py
import os
from PIL import Image
import fitz  # PyMuPDF for PDFs

def generate_thumbnail(input_path: str, output_path: str, size=(300, 300)):
    ext = os.path.splitext(input_path)[1].lower()

    if ext == ".pdf":
        pdf_document = fitz.open(input_path)
        page = pdf_document[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # higher resolution
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    else:
        img = Image.open(input_path)

    img.thumbnail(size)
    img.save(output_path, "PNG")
