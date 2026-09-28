from dataclasses import dataclass

from property_watch.db import cursor

PAIR_SQL = """
SELECT new.print_key_code, new.municipality_name,
       new.address_number, new.address_street,
       old.owner_name        AS old_owner,   new.owner_name        AS new_owner,
       old.assessment_total  AS old_assess,  new.assessment_total  AS new_assess
FROM parcels new
LEFT JOIN parcels old
       ON old.print_key_code = new.print_key_code AND old.roll_year = %(old_year)s
WHERE new.roll_year = %(new_year)s
"""


@dataclass
class Change:
    print_key_code: str
    kind: str
    address: str
    municipality: str
    old_value: str | None
    new_value: str | None
    pct: float | None = None


def _pct(old, new) -> float | None:
    if not old or new is None:
        return None
    return round((new - old) / old * 100, 1)


def classify(pair: dict, threshold_pct: float = 10.0) -> list[Change]:
    """Pure function: one joined row in, zero or more Changes out."""
    address = f"{pair.get('address_number') or ''} {pair.get('address_street') or ''}".strip()
    base = dict(print_key_code=pair["print_key_code"], address=address,
                municipality=pair.get("municipality_name") or "")
    out: list[Change] = []

    if pair["old_assess"] is None and pair["old_owner"] is None:
        return [Change(kind="new_parcel", old_value=None,
                       new_value=str(pair["new_assess"]), **base)]

    pct = _pct(pair["old_assess"], pair["new_assess"])
    if pct is not None and abs(pct) >= threshold_pct:
        out.append(Change(kind="assessment_up" if pct > 0 else "assessment_down",
                          old_value=str(pair["old_assess"]),
                          new_value=str(pair["new_assess"]), pct=pct, **base))

    if pair["old_owner"] and pair["new_owner"] and pair["old_owner"] != pair["new_owner"]:
        out.append(Change(kind="owner_changed", old_value=pair["old_owner"],
                          new_value=pair["new_owner"], **base))
    return out


def find_changes(old_year: int, new_year: int, threshold_pct: float = 10.0) -> list[Change]:
    with cursor() as cur:
        cur.execute(PAIR_SQL, {"old_year": old_year, "new_year": new_year})
        pairs = cur.fetchall()
    changes: list[Change] = []
    for pair in pairs:
        changes.extend(classify(pair, threshold_pct))
    return changes