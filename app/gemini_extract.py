from google import genai
from dotenv import load_dotenv
import os
import logging
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

model = "gemini-2.0-flash"

class ExtractedFields(BaseModel):
    room_rent_capping: str
    icu_capping: str
    maternity_capping: str
    ambulance_surcharge_capping: str
    daily_cash_benefit: str
    co_payment: str
    organ_donor_expenses_capping: str
    patient_onboarding_fee: str

def extract_fields_with_gemini(prompt):
    logger.info("Calling Gemini API...")
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": ExtractedFields
            }
        )

        logger.info("Gemini API call successful.")
        return response.text
    except Exception as e:
        logger.error(f"Error during Gemini extraction: {e}")
        return None