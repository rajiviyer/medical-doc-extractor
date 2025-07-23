import os
import logging
from dotenv import load_dotenv
from loader import extract_text_from_pdfs
from openai_extract import extract_fields_with_openai
from mistral_extract import extract_fields_with_mistral
from prompts import get_extraction_prompt
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

logger.info("Starting main extraction pipeline...")

try:
    merged_text = extract_text_from_pdfs("../docs")
    prompt = get_extraction_prompt(merged_text)
    logger.info("Files loaded. Beginning extraction...")
    result_json_openai = extract_fields_with_openai(prompt)
    result_json_mistral = extract_fields_with_mistral(prompt)

    os.makedirs("output", exist_ok=True)
    with open("output/extracted_summary_openai.json", "w") as f:
        f.write(result_json_openai)

    print("✅ Extracted fields saved to output/extracted_summary_openai.json")

    with open("output/extracted_summary_mistral.json", "w") as f:
        f.write(result_json_mistral)

    print("✅ Extracted fields saved to output/extracted_summary_mistral.json")
except Exception as e:
    logger.error(f"Error in main extraction pipeline: {e}")
