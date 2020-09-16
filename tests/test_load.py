from aphp import load

# This file tests that the different load functions can be called without
# generating errors


def test_load_raw_patients():
    df = load.load_raw_patients()
    assert not df.empty


def test_load_raw_tests():
    df = load.load_raw_tests()
    assert not df.empty


def test_load_clean_patients():
    df = load.load_clean_patients()
    assert not df.empty


def test_load_clean_tests():
    df = load.load_clean_tests()
    assert not df.empty


def test_load_deduplicated():
    df = load.load_deduplicated_patients()
    assert not df.empty


def test_load_analysis_dataset():
    df = load.load_patient_test_results()
    assert not df.empty
