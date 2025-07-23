def get_extraction_prompt(doc_text):
    return f"""
You are a health insurance analyst.

Your task is to extract the following fields from the document text:
- room_rent_capping
- icu_capping
- maternity_capping
- ambulance_surcharge_capping
- daily_cash_benefit
- co_payment
- organ_donor_expenses_capping
- patient_onboarding_fee

Extract only what is explicitly or clearly implied in the text. If something is not found, return "Not Mentioned".

Return the result as a valid JSON object.

Document:
\"\"\"
{doc_text}
\"\"\"
"""
