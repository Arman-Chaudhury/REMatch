from property_watch.db import cursor

UPSERT_SQL = """
INSERT INTO parcels (
    print_key_code, roll_year, municipality_name, swis_code, 
    property_class, property_class_desc, address_number, address_street,
    owner_name, zip, full_market_value, assessment_land, assessment_total
) VALUES (
    %(print_key_code)s, %(roll_year)s, %(municipality_name)s, %(swis_code)s,
    %(property_class)s, %(property_class_desc)s, %(address_number)s, %(address_street)s,
    %(owner_name)s, %(zip)s, %(full_market_value)s, %(assessment_land)s, %(assessment_total)s
)
ON CONFLICT (print_key_code, roll_year) DO UPDATE SET
    owner_name              =EXCLUDED.owner_name,
    full_market_value       =EXCLUDED.full_market,
    assessment_land         =EXCLUDED.assessment_land,
    assessment_total        =EXCLUDED.assessment_total,
    fetched_at              =now()
"""

def _int(value) -> int | None:
    try:
        return int(float(value)) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None

def to_row(api: dict) -> dict: 
    return {
        "print_key_code": api["print_key_code"],
        "roll_year": _int(api["roll_year"]),
        "municipality_name": api.get("municipality_name"),
        "swis_code": api.get("swis_code"),
        "property_class": api.get("property_class"),
        "property_class_desc": api.get("property_class_desc"),
        "address_number": api.get("address_number"),
        "address_street": api.get("address_street"),
        "owner_name":api.get("owner_name"),
        "zip": api.get("mailing_address_zip"),
        "full_market_value": api.get("full_market_value"),
        "assessment_land": _int(api.get("assessment_land")),
        "assessment_total": _int(api.get("assessment_total"))
    }

def store_rows(api_rows: list[dict]) -> int:
    rows = [to_row(r) for r in api_rows if r.get("print_key_code")]
    with cursor() as cur:
        cur.executemany(UPSERT_SQL, rows)
    return len(rows)