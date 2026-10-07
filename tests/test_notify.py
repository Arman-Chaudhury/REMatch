from property_watch.notify import build_message


def test_one_email_lists_every_change():
    items = [
        {"title": "Ownership change recorded for 16 PUTNAM AVE, Glen Cove", "summary": "New owner."},
        {"title": "Assessment rose 30% at 26 CROW LN, Glen Cove", "summary": "Value rose."},
    ]
    msg = build_message("watcher@example.com", items)
    body = msg.get_content()
    assert msg["To"] == "watcher@example.com"
    assert msg["Subject"] == "REMatch: 2 change(s) at addresses you watch"
    assert "16 PUTNAM AVE" in body and "26 CROW LN" in body
