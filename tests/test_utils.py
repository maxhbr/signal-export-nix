from sigexport import utils


def test_source_location():
    utils.source_location()


def test_timestamp_format():
    dt = utils.dt_from_ts(76823746823)
    res = utils.timestamp_format(dt)
    assert res == "1972-06-08 03:55"
