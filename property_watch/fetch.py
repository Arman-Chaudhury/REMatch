import httpx

API_URL = "https://data.ny.gov/resource/7vem-aaz7.json"

FIELDS = [
    "roll_year", "print_key_code", "municipality_name", "swiss_code", 
    "property_class", "property_class_description", "parcel_address_number", "parcel_address_street",
    "primary_owner_last_name", "mailing_address_zip", "full_market_value", "assessment_land", "assessment_total"
]