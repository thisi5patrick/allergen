from enum import StrEnum


class ActiveTab(StrEnum):
    OVERVIEW = "overview"
    SYMPTOMS = "symptoms"
    FOOD_ALLERGIES = "food_allergies"
    MEDICATIONS = "medications"
    CHANGE_PASSWORD = "change_password"
    DELETE_ACCOUNT = "delete_account"
