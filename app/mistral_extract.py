import os
import logging
from mistralai import Mistral
from dotenv import load_dotenv
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

logger.info("Starting Mistral extraction...")

client = Mistral(api_key=MISTRAL_API_KEY)

class ExtractedFields(BaseModel):
    room_rent_capping: str
    icu_capping: str
    maternity_capping: str
    ambulance_surcharge_capping: str
    daily_cash_benefit: str
    co_payment: str
    organ_donor_expenses_capping: str
    patient_onboarding_fee: str

def extract_fields_with_mistral(prompt):
    logger.info("Calling Mistral API...")    
    try:
        response = client.chat.complete(
            model="mistral-large-latest", 
            messages=[{"role": "user", "content": prompt}])
    except Exception as e:
        logger.error(f"Error during Mistral extraction: {e}")
        return None
    logger.info("Mistral API call successful.")
    return response.choices[0].message.content