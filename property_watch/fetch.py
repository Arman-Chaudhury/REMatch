import httpx
import time


API_URL = "https://data.ny.gov/resource/7vem-aaz7.json"

FIELDS = [
    "roll_year", "print_key_code", "municipality_name", "swis_code",
    "property_class", "property_class_description", "parcel_address_number", "parcel_address_street",
    "primary_owner_last_name", "mailing_address_zip", "full_market_value", "assessment_land", "assessment_total"
]

RETRYABLE = {429, 500, 502, 503,504}

def fetch_page(roll_year:int, limit: int= 100, offset: int = 0, municipality_name: str | None = None, attempts: int = 3) -> list[dict]:
    params = {
        "county_name": "Nassau",
        "roll_year":str(roll_year),
        "$select": ",".join(FIELDS),
        "$order":"print_key_code",
        "$limit":str(limit), 
        "$offset": str(offset),
        
    }
    if municipality_name: 
        params["municipality_name"] = municipality_name

    for attempt in range(attempts):
        try:
            response = httpx.get(API_URL, params= params, timeout=60)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            last_attempt = attempt == attempts -1
            if status not in RETRYABLE or last_attempt:
                raise
            delay = 2 ** attempt
            print(f"HTTP {status}; retrying in {delay}s", flush = True)
            time.sleep(delay)

def fetch_all(roll_year: int, page_size: int = 5000, pause_sec: float = 0.5):
    offset = 0
    while True: 
        page = fetch_page(roll_year, limit= page_size, offset=offset)
        if not page:
            return
        yield from page
        if len(page) < page_size:
            return
        offset += page_size
        time.sleep(pause_sec)