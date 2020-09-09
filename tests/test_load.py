from aphp import load


def test_load_raw():
    df = load.load_raw_patients()
    assert not df.empty

    df = load.load_raw_tests()
    assert not df.empty
