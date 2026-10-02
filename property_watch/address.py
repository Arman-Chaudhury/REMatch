"""Normalize street addresses so '26 Crow Lane' == '26 CROW LN'."""

import re

# Every spelling -> the form the roll uses most (checked against 2025 data).
SUFFIXES = {
    "AVENUE": "AVE", "AV": "AVE",
    "STREET": "ST",
    "ROAD": "RD",
    "DRIVE": "DR",
    "LANE": "LN", "LA": "LN",
    "PLACE": "PL",
    "BOULEVARD": "BLVD",
    "COURT": "CT",
    "PARKWAY": "PKWY",
    "TURNPIKE": "TPKE",
    "CIRCLE": "CIR",
    "TERRACE": "TER",
    "HIGHWAY": "HWY",
    "CRESCENT": "CRES",
    "RIDGE": "RDG",
}


def normalize(address: str) -> str:
    words = re.sub(r"[.,#]", " ", address.upper()).split()
    return " ".join(SUFFIXES.get(w, w) for w in words)
