from property_watch.changes import describe
from property_watch.diff import classify


def pair(**overrides):
    base = {
        "swis_code": "280600",
        "print_key_code": "1-2-3",
        "municipality_name": "Glen Cove",
        "address_number": "26",
        "address_street": "CROW LA",
        "old_owner": "SMITH",
        "new_owner": "SMITH",
        "old_assess": 100_000,
        "new_assess": 100_000,
    }
    return {**base, **overrides}


def test_no_change_yields_nothing():
    assert classify(pair()) == []


def test_owner_change_detected():
    (c,) = classify(pair(new_owner="JONES"))
    assert c.kind == "owner_changed"
    assert c.old_value == "SMITH" and c.new_value == "JONES"
    assert c.address == "26 CROW LA"


def test_change_keeps_town_code():
    (c,) = classify(pair(new_owner="JONES"))
    assert (c.swis_code, c.print_key_code) == ("280600", "1-2-3")


def test_assessment_rise_over_threshold():
    (c,) = classify(pair(new_assess=125_000))
    assert c.kind == "assessment_up" and c.pct == 25.0


def test_small_move_ignored():
    assert classify(pair(new_assess=105_000)) == []


def test_new_parcel():
    (c,) = classify(pair(old_owner=None, old_assess=None))
    assert c.kind == "new_parcel"


def test_new_parcel_without_assessment_has_none_value():
    (c,) = classify(pair(old_owner=None, old_assess=None, new_assess=None))
    assert c.kind == "new_parcel"
    assert c.new_value is None


def test_describe_new_parcel_without_assessment_does_not_raise():
    (c,) = classify(pair(old_owner=None, old_assess=None, new_assess=None))
    title, summary, _ = describe(c, 2025)
    assert title.startswith("New parcel on the 2025 roll")
    assert "$0" not in summary and "None" not in summary
    assert "not yet listed" in summary


def test_describe_new_parcel_with_assessment():
    (c,) = classify(pair(old_owner=None, old_assess=None, new_assess=250_000))
    _, summary, _ = describe(c, 2025)
    assert "assessed at $250,000" in summary


def test_owner_and_assessment_both_change():
    kinds = {c.kind for c in classify(pair(new_owner="JONES", new_assess=60_000))}
    assert kinds == {"owner_changed", "assessment_down"}
