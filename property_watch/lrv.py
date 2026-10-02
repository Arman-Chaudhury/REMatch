"""Sale history from Nassau County's Land Records Viewer (LRV).

The state API has owners and values but no sale prices; the county site has
both. We scrape only parcels someone is watching, one page every few seconds,
and never touch the CAPTCHA-protected search.
"""

import re
import time
from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from property_watch.db import cursor

BASE_URL = "https://lrv.nassaucountyny.gov"
USER_AGENT = "REMatch/0.1 (+https://github.com/Arman-Chaudhury/REMatch)"

SAVE_SQL = """
INSERT INTO sales (print_key_code, sale_date, price, book, page, condition)
VALUES (%(print_key_code)s, %(sale_date)s, %(price)s, %(book)s, %(page)s, %(condition)s)
ON CONFLICT (print_key_code, sale_date, book, page) DO NOTHING
"""

WATCHED_SQL = """
SELECT DISTINCT c.print_key_code
FROM notifications n
JOIN changes c ON c.id = n.change_id
WHERE c.kind = 'owner_changed'
"""


def to_sbl(print_key_code: str) -> str:
    """'21.-222-464' -> '21222  04640', the county's fixed-width parcel ID.

    Layout: section (2) + block (5) + lot (4) + sublot (1). Numeric blocks are
    zero-padded to 3 (or 5 if longer), letter blocks right-aligned in 3.
    Checked against the live site for numeric, letter, 4-digit and lettered-lot cases.
    """
    if "/" in print_key_code:
        raise ValueError(f"no county page for split parcel {print_key_code}")
    section, block, lot = print_key_code.split("-", 2)
    section = section.rstrip(".").zfill(2)
    if block.isdigit():
        block = block.zfill(3) if len(block) <= 3 else block.zfill(5)
    else:
        block = block.rjust(3)
    number, _, sublot = lot.partition(".")
    return f"{section}{block.ljust(5)}{number.zfill(4)}{sublot or '0'}"


def parse_sales(html: str) -> list[dict]:
    """Rows of the page's Sales History table, oldest last as the site lists them."""
    pane = BeautifulSoup(html, "html.parser").find(id="infosalestab")
    if pane is None:
        return []
    sales = []
    for tr in pane.select("tbody tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(cells) != 5:
            continue
        date, price, book, page, condition = cells
        try:
            sale_date = datetime.strptime(date, "%m/%d/%Y").date()
        except ValueError:
            continue
        digits = re.sub(r"\D", "", price)
        sales.append({
            "sale_date": sale_date,
            "price": int(digits) if digits else None,
            "book": book,
            "page": page,
            "condition": condition or None,
        })
    return sales


def fetch_sales(print_keys: list[str], pause_sec: float = 3.0):
    """Yield (print_key_code, sales) for each parcel, one polite request at a time."""
    headers = {"User-Agent": USER_AGENT}
    with httpx.Client(base_url=BASE_URL, headers=headers,
                      follow_redirects=True, timeout=30) as client:
        client.get("/")
        for key in print_keys:
            try:
                sbl = to_sbl(key)
            except ValueError:
                continue
            time.sleep(pause_sec)
            response = client.get(f"/info/{sbl.replace(' ', '+')}/")
            response.raise_for_status()
            yield key, parse_sales(response.text)


def save_sales(print_key_code: str, sales: list[dict]) -> int:
    """Insert sales; return how many were new."""
    written = 0
    with cursor() as cur:
        for s in sales:
            cur.execute(SAVE_SQL, {"print_key_code": print_key_code, **s})
            written += cur.rowcount
    return written


def watched_sold_parcels() -> list[str]:
    """Parcels whose ownership change was matched to someone's watch."""
    with cursor() as cur:
        cur.execute(WATCHED_SQL)
        return [r["print_key_code"] for r in cur.fetchall()]
