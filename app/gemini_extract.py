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
    base_sum_assured: str
    room_rent_capping: str
    icu_capping: str
    room_category_capping: str
    medical_practitioners_capping: str
    treatment_related_to_participation_as_a_non_professional_in_hazardous_or_adventure_sports: str
    other_expenses_capping: str
    modern_treatment_capping: str
    cataract_capping: str
    hernia_capping: str
    joint_replacement_capping: str
    any_kind_of_surgery_specific_capping: str
    treatment_based_capping_dialysis: str
    treatment_based_capping_chemotherapy: str
    treatment_based_capping_radiotherapy: str
    consumable_and_non_medical_items_capping: str
    maternity_capping: str
    ambulance_charge_capping: str
    daily_cash_benefit: str
    co_payment: str
    opd_daycare_domiciliary_treatment_capping: str
    pre_post_hospitalization_expenses_capping: str
    diagnostic_tests_and_investigation_capping: str
    implants_stents_prosthetics_capping: str
    mental_illness_treatment_capping: str
    organ_donor_expenses_capping: str
    bariatric_obesity_surgery_capping: str
    cancer_treatment_capping_in_specific_plans: str
    internal_congenital_disease_capping: str
    ayush_hospitalization_capping: str
    vaccination_preventive_health_check_up_capping: str
    artificial_prostheses_aids_capping: str

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