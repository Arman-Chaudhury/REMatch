from property_watch.diff import classify


def pair(**overrides):
    base = dict(print_key_code="1-2-3", municipality_name="Glen Cove",
                address_number="26", address_street="CROW LA",
                old_owner="SMITH", new_owner="SMITH",
                old_assess=100_000, new_assess=100_000)
    return {**base, **overrides}


def test_no_change_yields_nothing():
    assert classify(pair()) == []


def test_owner_change_detected():
    (c,) = classify(pair(new_owner="JONES"))
    assert c.kind == "owner_changed"
    assert c.old_value == "SMITH" and c.new_value == "JONES"
    assert c.address == "26 CROW LA"


def test_assessment_rise_over_threshold():
    (c,) = classify(pair(new_assess=125_000))
    assert c.kind == "assessment_up" and c.pct == 25.0


def test_small_move_ignored():
    assert classify(pair(new_assess=105_000)) == []


def test_new_parcel():
    (c,) = classify(pair(old_owner=None, old_assess=None))
    assert c.kind == "new_parcel"


def test_owner_and_assessment_both_change():
    kinds = {c.kind for c in classify(pair(new_owner="JONES", new_assess=60_000))}
    assert kinds == {"owner_changed", "assessment_down"}