from property_watch.address import normalize


def test_typed_address_matches_roll_form():
    assert normalize("26 Crow Lane") == normalize("26 CROW LN") == "26 CROW LN"


def test_punctuation_and_extra_spaces_ignored():
    assert normalize("12  Main St., #2") == "12 MAIN ST 2"


def test_words_that_are_not_suffixes_left_alone():
    assert normalize("100 Broadway") == "100 BROADWAY"
