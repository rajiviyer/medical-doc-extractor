def get_openai_policy_prompt(metadata_list_json):
    return f"""
You are a health insurance analyst specializing in policy document analysis.

You are given a list of master policy documents text segments, each with metadata about its source file, extraction method, and extraction success. 

Your task is to extract information for the following fields from the document.
If a field is not found, return null.

IMPORTANT: Return a valid JSON object with these exact field names as keys:
- base_sum_assured: Base Sum Assured/Base Sum Insured
- room_rent_capping: Cap on room rent
- icu_capping: Cap on ICU charges
- room_category_capping: Cap on room category
- medical_practitioners_capping: Cap on medical practitioners
- treatment_related_to_participation_as_a_non_professional_in_hazardous_or_adventure_sports
- other_expenses_capping: Cap on other expenses
- modern_treatment_capping: Cap on modern treatment
- cataract_capping: Cap on cataract
- hernia_capping: Cap on hernia
- joint_replacement_capping: Cap on joint replacement
- any_kind_of_surgery_specific_capping: Cap on any kind of surgery
- treatment_based_capping_dialysis: Cap on treatment based capping dialysis
- treatment_based_capping_chemotherapy: Cap on treatment based capping chemotherapy
- treatment_based_capping_radiotherapy: Cap on treatment based capping radiotherapy
- consumable_and_non_medical_items_capping: Cap on consumable and non medical items
- maternity_capping: Cap on maternity
- ambulance_charge_capping: Cap on ambulance charge
- daily_cash_benefit: Cap on daily cash benefit
- co_payment: Cap on co payment
- opd_daycare_domiciliary_treatment_capping: Cap on OPD, Daycare, Domiciliary treatment
- pre_post_hospitalization_expenses_capping: Cap on pre and post hospitalization expenses
- diagnostic_tests_and_investigation_capping: Cap on diagnostic tests and investigation
- implants_stents_prosthetics_capping: Cap on implants, stents, prosthetics
- mental_illness_treatment_capping: Cap on mental illness treatment
- organ_donor_expenses_capping: Cap on organ donor expenses
- bariatric_obesity_surgery_capping: Cap on bariatric, obesity surgery
- cancer_treatment_capping_in_specific_plans: Cap on cancer treatment in specific plans
- internal_congenital_disease_capping: Cap on internal, congenital disease
- ayush_hospitalization_capping: Cap on ayush hospitalization
- vaccination_preventive_health_check_up_capping: Cap on vaccination, preventive health check up
- artificial_prostheses_aids_capping: Cap on artificial prostheses, aids

Here is the list of policy document segments (as JSON):
{metadata_list_json}
"""

def get_mistral_policy_prompt(metadata_list_json):
    return f"""
You are a health insurance analyst specializing in policy document analysis.

You are given a list of policy document text segments, each with metadata about its source file, extraction method, and extraction success. 

Your task is to extract information for the following fields from the policy documents and 
based on the information, calculate or infer the capping values.
If information for a field is not found, return null.

IMPORTANT: Return a valid JSON object with these exact field names as keys:
- base_sum_assured: Base Sum Assured/Base Sum Insured
- room_rent_capping: Cap on room rent
- icu_capping: Cap on ICU charges
- room_category_capping: Cap on room category
- medical_practitioners_capping: Cap on medical practitioners
- treatment_related_to_participation_as_a_non_professional_in_hazardous_or_adventure_sports: Cap on treatment related to participation as a non professional in hazardous or adventure sports
- other_expenses_capping: Cap on other expenses
- modern_treatment_capping: Cap on modern treatment
- cataract_capping: Cap on cataract
- hernia_capping: Cap on hernia
- joint_replacement_capping: Cap on joint replacement
- any_kind_of_surgery_specific_capping: Cap on any kind of surgery
- treatment_based_capping_dialysis: Cap on treatment based capping dialysis
- treatment_based_capping_chemotherapy: Cap on treatment based capping chemotherapy
- treatment_based_capping_radiotherapy: Cap on treatment based capping radiotherapy
- consumable_and_non_medical_items_capping: Cap on consumable and non medical items
- maternity_capping: Cap on maternity
- ambulance_charge_capping: Cap on ambulance charge
- daily_cash_benefit: Cap on daily cash benefit
- co_payment: Cap on co payment
- opd_daycare_domiciliary_treatment_capping: Cap on OPD, Daycare, Domiciliary treatment
- pre_post_hospitalization_expenses_capping: Cap on pre and post hospitalization expenses
- diagnostic_tests_and_investigation_capping: Cap on diagnostic tests and investigation
- implants_stents_prosthetics_capping: Cap on implants, stents, prosthetics
- mental_illness_treatment_capping: Cap on mental illness treatment
- organ_donor_expenses_capping: Cap on organ donor expenses
- bariatric_obesity_surgery_capping: Cap on bariatric, obesity surgery
- cancer_treatment_capping_in_specific_plans: Cap on cancer treatment in specific plans
- internal_congenital_disease_capping: Cap on internal, congenital disease
- ayush_hospitalization_capping: Cap on ayush hospitalization
- vaccination_preventive_health_check_up_capping: Cap on vaccination, preventive health check up
- artificial_prostheses_aids_capping: Cap on artificial prostheses, aids

Here is the list of policy document segments (as JSON):
{metadata_list_json}
"""

def get_gemini_policy_prompt(metadata_list_json):
    return f"""
You are a health insurance analyst specializing in policy document analysis.

You are given a list of policy document text segments, each with metadata about its source file, extraction method, and extraction success. 

Your task is to extract information for the following fields from the policy documents and 
based on the information, calculate or infer the capping values.
If information for a field is not found, return null.

IMPORTANT: Return a valid JSON object matching the ExtractedFields schema with these exact field names as keys:

- base_sum_assured: Base Sum Assured/Base Sum Insured
- room_rent_capping: Cap on room rent
- icu_capping: Cap on ICU charges
- room_category_capping: Cap on room category
- medical_practitioners_capping: Cap on medical practitioners
- treatment_related_to_participation_as_a_non_professional_in_hazardous_or_adventure_sports: Cap on treatment related to participation as a non professional in hazardous or adventure sports
- other_expenses_capping: Cap on other expenses
- modern_treatment_capping: Cap on modern treatment
- cataract_capping: Cap on cataract
- hernia_capping: Cap on hernia
- joint_replacement_capping: Cap on joint replacement
- any_kind_of_surgery_specific_capping: Cap on any kind of surgery
- treatment_based_capping_dialysis: Cap on treatment based capping dialysis
- treatment_based_capping_chemotherapy: Cap on treatment based capping chemotherapy
- treatment_based_capping_radiotherapy: Cap on treatment based capping radiotherapy
- consumable_and_non_medical_items_capping: Cap on consumable and non medical items
- maternity_capping: Cap on maternity
- ambulance_charge_capping: Cap on ambulance charge
- daily_cash_benefit: Cap on daily cash benefit
- co_payment: Cap on co payment
- opd_daycare_domiciliary_treatment_capping: Cap on OPD, Daycare, Domiciliary treatment
- pre_post_hospitalization_expenses_capping: Cap on pre and post hospitalization expenses
- diagnostic_tests_and_investigation_capping: Cap on diagnostic tests and investigation
- implants_stents_prosthetics_capping: Cap on implants, stents, prosthetics
- mental_illness_treatment_capping: Cap on mental illness treatment
- organ_donor_expenses_capping: Cap on organ donor expenses
- bariatric_obesity_surgery_capping: Cap on bariatric, obesity surgery
- cancer_treatment_capping_in_specific_plans: Cap on cancer treatment in specific plans
- internal_congenital_disease_capping: Cap on internal, congenital disease
- ayush_hospitalization_capping: Cap on ayush hospitalization
- vaccination_preventive_health_check_up_capping: Cap on vaccination, preventive health check up
- artificial_prostheses_aids_capping: Cap on artificial prostheses, aids

Here is the list of policy document segments (as JSON):
{metadata_list_json}
"""