import httpx

API_URL = "https://data.ny.gov/resource/7vem-aaz7.json"

FIELDS = [
    "roll_year", "print_key_code", "municipality_name", "swis_code",
    "property_class", "property_class_description", "parcel_address_number", "parcel_address_street",
    "primary_owner_last_name", "mailing_address_zip", "full_market_value", "assessment_land", "assessment_total"
]

def fetch_page(roll_year:int, limit: int= 100, offset: int = 0, municipality_name: str | None = None) -> list[dict]:
    params = {
        "county_name": "Nassau",
        "roll_year":str(roll_year),
        "$select": ",".join(FIELDS),
        "$order":"print_key_code",
        "$limit":str(limit), 
        "$offset": str(offset),
        
    }
    if municipality_name: params["municipality_name"] = municipality_name
    response = httpx.get(API_URL, params= params, timeout=60)
    response.raise_for_status()
    return response.json()