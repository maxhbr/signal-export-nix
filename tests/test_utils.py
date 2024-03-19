from sigexport.utils import source_location, timestamp_format


def test_source_location():
    source_location()


def test_timestamp_format():
    res = timestamp_format(76823746823)
    assert res == "1972-06-08 03:55"
