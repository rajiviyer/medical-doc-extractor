import os
import pdfplumber
from utils import ocr_from_image, ocr_from_scanned_pdf
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdfs(folder_path):
    combined_text = ""
    for file in sorted(os.listdir(folder_path)):
        path = os.path.join(folder_path, file)

        if file.endswith(".pdf"):
            try:
                logger.info(f"Extracting text from {path}")
                with pdfplumber.open(path) as pdf:
                    extracted = "\n".join([page.extract_text() or "" for page in pdf.pages])
                    if extracted.strip():
                        combined_text += extracted + "\n"
                        # logger.info(f"Extracted text: {extracted}")
                    else:
                        logger.info(f"Text not found in {path}. Attempting OCR.")
                        ocr_text = ocr_from_scanned_pdf(path)   
                        if ocr_text:
                            combined_text += ocr_text + "\n"
                            logger.info(f"OCR text: {ocr_text}")
                        else:
                            logger.error(f"OCR failed for {path}")
            except Exception as e:
                logger.error(f"Error extracting text from {path}: {e}")
                ocr_text = ocr_from_scanned_pdf(path)
                if ocr_text:
                    combined_text += ocr_text + "\n"
                    logger.info(f"OCR text: {ocr_text}")
                else:
                    logger.error(f"OCR failed for {path}")

        elif file.lower().endswith((".jpg", ".jpeg", ".png")):
            logger.info(f"Extracting text from {path}")
            ocr_text = ocr_from_image(path) 
            if ocr_text:
                combined_text += ocr_text + "\n"
                logger.info(f"OCR text: {ocr_text}")
            else:
                logger.error(f"OCR failed for {path}")

    return combined_text
