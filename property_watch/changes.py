from property_watch.db import cursor
from property_watch.diff import Change

INSERT_SQL = """
INSERT INTO changes (
    swis_code, print_key_code, roll_year, kind, municipality, address,
    old_value, new_value, pct, title, summary, impact
) VALUES (
    %(swis_code)s, %(print_key_code)s, %(roll_year)s, %(kind)s, %(municipality)s, %(address)s,
    %(old_value)s, %(new_value)s, %(pct)s, %(title)s, %(summary)s, %(impact)s
)
ON CONFLICT (swis_code, print_key_code, roll_year, kind) DO NOTHING
"""

def describe(c: Change, new_year: int) -> tuple[str, str, str]:
    where= f"{c.address}, {c.municipality}".strip(", ")
    if c.kind == "owner_changed":
        return (f"Ownership change recorded for {where}",
                f"The {new_year} assessment roll lists a new owner for {where} "
                f"({c.old_value} -> {c.new_value}), which usually indicates a sale.", "medium")
    if c.kind in ("assessment_up", "assessment_down"):
        direction = "rose" if c.kind == "assessment_up" else "fell"
        return (f"Assessment {direction} {abs(c.pct):.0f}% at {where}",
                f"Total assessed value {direction} from ${int(c.old_value):,} to "
                f"${int(c.new_value):,} on the {new_year} roll.",
                "high" if abs(c.pct) >= 25 else "medium")
    return (f"New parcel on the {new_year} roll: {where}",
            f"{where} appears for the first time on the {new_year} assessment roll "
            f"(assessed at ${int(c.new_value or 0):,}).", "low")


def save_changes(changes: list[Change], new_year: int) -> int:
    """Insert changes; return how many were new."""
    written = 0
    with cursor() as cur:
        for c in changes:
            title, summary, impact = describe(c, new_year)
            cur.execute(INSERT_SQL, {
                "swis_code": c.swis_code, "print_key_code": c.print_key_code,
                "roll_year": new_year, "kind": c.kind,
                "municipality": c.municipality or None, "address": c.address or None,
                "old_value": c.old_value, "new_value": c.new_value, "pct": c.pct,
                "title": title[:300], "summary": summary, "impact": impact,
            })
            written += cur.rowcount
    return written