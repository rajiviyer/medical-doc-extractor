from pydantic import BaseModel, Field
from typing import Optional

class ExtractedFields(BaseModel):
    """Schema for extracted policy fields from LLM responses."""
    base_sum_assured: str = Field(description="Base Sum Assured/Base Sum Insured")
    room_rent_capping: str = Field(description="Cap on room rent")
    icu_capping: str = Field(description="Cap on ICU charges")
    room_category_capping: str = Field(description="Cap on room category")
    medical_practitioners_capping: str = Field(description="Cap on medical practitioners")
    treatment_related_to_participation_as_a_non_professional_in_hazardous_or_adventure_sports: str = Field(description="Cap on treatment related to participation as a non professional in hazardous or adventure sports")
    other_expenses_capping: str = Field(description="Cap on other expenses")
    modern_treatment_capping: str = Field(description="Cap on modern treatment")
    cataract_capping: str = Field(description="Cap on cataract")
    hernia_capping: str = Field(description="Cap on hernia")
    joint_replacement_capping: str = Field(description="Cap on joint replacement")
    any_kind_of_surgery_specific_capping: str = Field(description="Cap on any kind of surgery")
    treatment_based_capping_dialysis: str = Field(description="Cap on treatment based capping dialysis")
    treatment_based_capping_chemotherapy: str = Field(description="Cap on treatment based capping chemotherapy")
    treatment_based_capping_radiotherapy: str = Field(description="Cap on treatment based capping radiotherapy")
    consumable_and_non_medical_items_capping: str = Field(description="Cap on consumable and non medical items")
    maternity_capping: str = Field(description="Cap on maternity")
    ambulance_charge_capping: str = Field(description="Cap on ambulance charge")
    daily_cash_benefit: str = Field(description="Cap on daily cash benefit")
    co_payment: str = Field(description="Cap on co payment")
    opd_daycare_domiciliary_treatment_capping: str = Field(description="Cap on OPD, Daycare, Domiciliary treatment")
    pre_post_hospitalization_expenses_capping: str = Field(description="Cap on pre and post hospitalization expenses")
    diagnostic_tests_and_investigation_capping: str = Field(description="Cap on diagnostic tests and investigation")
    implants_stents_prosthetics_capping: str = Field(description="Cap on implants, stents, prosthetics")
    mental_illness_treatment_capping: str = Field(description="Cap on mental illness treatment")
    organ_donor_expenses_capping: str = Field(description="Cap on organ donor expenses")
    bariatric_obesity_surgery_capping: str = Field(description="Cap on bariatric, obesity surgery")
    cancer_treatment_capping_in_specific_plans: str = Field(description="Cap on cancer treatment in specific plans")
    internal_congenital_disease_capping: str = Field(description="Cap on internal, congenital disease")
    ayush_hospitalization_capping: str = Field(description="Cap on ayush hospitalization")
    vaccination_preventive_health_check_up_capping: str = Field(description="Cap on vaccination, preventive health check up")
    artificial_prostheses_aids_capping: str = Field(description="Cap on artificial prostheses, aids")
    policy_start_date: str = Field(description="Policy start date")
    policy_end_date: str = Field(description="Policy end date")
    date_of_admission: str = Field(description="Date of admission to hospital")

    class Config:
        """Pydantic configuration."""
        extra = "ignore"  # Ignore extra fields for API compatibility
        validate_assignment = True  # Validate on assignment 