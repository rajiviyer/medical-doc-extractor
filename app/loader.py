import os
import pdfplumber
from utils import ocr_from_image, ocr_from_scanned_pdf

def extract_text_from_pdfs(folder_path):
    combined_text = ""
    for file in sorted(os.listdir(folder_path)):
        path = os.path.join(folder_path, file)

        if file.endswith(".pdf"):
            try:
                # Try text-based extraction
                with pdfplumber.open(path) as pdf:
                    extracted = "\n".join([page.extract_text() or "" for page in pdf.pages])
                    if extracted.strip():
                        combined_text += extracted + "\n"
                    else:
                        raise ValueError("Text not found. Attempting OCR.")
            except:
                combined_text += ocr_from_scanned_pdf(path)

        elif file.lower().endswith((".jpg", ".jpeg", ".png")):
            combined_text += ocr_from_image(path) + "\n"

    return combined_text
