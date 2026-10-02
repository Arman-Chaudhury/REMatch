"""Connect watches to changes at the same address."""

from property_watch.address import normalize
from property_watch.db import cursor

MATCH_SQL = """
INSERT INTO notifications (watch_id, change_id)
SELECT w.id, c.id
FROM watches w
JOIN changes c ON c.address_key = w.address_key
WHERE w.municipality IS NULL OR c.municipality ILIKE w.municipality
ON CONFLICT (watch_id, change_id) DO NOTHING
"""

PENDING_SQL = """
SELECT n.id, w.email, c.title, c.summary, c.impact
FROM notifications n
JOIN watches w ON w.id = n.watch_id
JOIN changes c ON c.id = n.change_id
ORDER BY n.id DESC
LIMIT %(limit)s
"""


def add_watch(email: str, address: str, municipality: str | None = None) -> int:
    with cursor() as cur:
        cur.execute(
            "INSERT INTO watches (email, address, address_key, municipality) "
            "VALUES (%s, %s, %s, %s) RETURNING id",
            (email, address, normalize(address), municipality),
        )
        return cur.fetchone()["id"]


def run_matching() -> int:
    with cursor() as cur:
        cur.execute(MATCH_SQL)
        return cur.rowcount


def pending(limit: int = 20) -> list[dict]:
    with cursor() as cur:
        cur.execute(PENDING_SQL, {"limit": limit})
        return cur.fetchall()
