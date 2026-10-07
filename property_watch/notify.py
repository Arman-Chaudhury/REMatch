"""Email unsent notifications to watchers. Prints instead of sending unless send=True."""

import os
import smtplib
from email.message import EmailMessage

from property_watch.db import cursor

UNSENT_SQL = """
SELECT n.id, w.email, c.title, c.summary
FROM notifications n
JOIN watches w ON w.id = n.watch_id
JOIN changes c ON c.id = n.change_id
WHERE n.sent_at IS NULL
ORDER BY w.email, n.id
"""

MARK_SENT_SQL = "UPDATE notifications SET sent_at = now() WHERE id = ANY(%s)"


def unsent() -> dict[str, list[dict]]:
    """Unsent notifications grouped by email address."""
    by_email: dict[str, list[dict]] = {}
    with cursor() as cur:
        cur.execute(UNSENT_SQL)
        for row in cur.fetchall():
            by_email.setdefault(row["email"], []).append(row)
    return by_email


def build_message(email: str, items: list[dict]) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = f"REMatch: {len(items)} change(s) at addresses you watch"
    msg["From"] = os.environ.get("SMTP_USER", "rematch@localhost")
    msg["To"] = email
    body = "\n\n".join(f"- {i['title']}\n  {i['summary']}" for i in items)
    msg.set_content(f"Changes on the Nassau County assessment roll:\n\n{body}\n")
    return msg


def send_pending(send: bool = False) -> int:
    """Email each watcher once; return how many emails went out."""
    groups = unsent()
    if not groups:
        return 0
    if not send:
        for email, items in groups.items():
            print(build_message(email, items))
            print("-" * 40)
        return 0
    sent = 0
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        for email, items in groups.items():
            smtp.send_message(build_message(email, items))
            with cursor() as cur:
                cur.execute(MARK_SENT_SQL, ([i["id"] for i in items],))
            sent += 1
    return sent
