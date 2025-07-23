import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import os

def ocr_from_image(image_path):
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)

def ocr_from_scanned_pdf(pdf_path):
    text = ""
    images = convert_from_path(pdf_path, dpi=300)
    for i, image in enumerate(images):
        text += pytesseract.image_to_string(image) + "\n"
    return text
