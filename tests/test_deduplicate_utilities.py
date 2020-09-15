import pandas as pd
import numpy as np

from aphp import deduplicate


def test_iter_pairs_of_rows_empty():
    df = pd.DataFrame()
    result = list(deduplicate._iter_pairs_of_rows(df))
    assert result == []

    df = pd.DataFrame([{"id": "A"}])
    result = list(deduplicate._iter_pairs_of_rows(df))
    assert result == []


def test_iter_pairs_of_rows():
    df = pd.DataFrame([{"id": "A"}, {"id": "B"}, {"id": "C"}])
    result = [
        row1["id"] + row2["id"] for row1, row2 in deduplicate._iter_pairs_of_rows(df)
    ]
    assert result == ["AB", "AC", "BC"]


def test_sorted_string():
    assert deduplicate._sorted_string("b a") == "a b"
    assert deduplicate._sorted_string("b", "a") == "a b"
    assert deduplicate._sorted_string("b", None) == "b"
    assert deduplicate._sorted_string("b", np.NaN, "a") == "a b"


def test_similar_fullname():
    patient_1 = pd.Series({"given_name": "benjamin", "surname": "habert"})

    patient_2 = pd.Series({"given_name": "habert", "surname": "benjamin"})
    assert deduplicate._similar_fullname(patient_1, patient_2)

    patient_2 = pd.Series({"given_name": "benjmin", "surname": "habert"})
    assert deduplicate._similar_fullname(patient_1, patient_2)

    patient_2 = pd.Series({"given_name": "benjmin", "surname": "haert"})
    assert deduplicate._similar_fullname(patient_1, patient_2)

    patient_2 = pd.Series({"given_name": "bnjmin", "surname": "haert"})
    assert deduplicate._similar_fullname(patient_1, patient_2)

    patient_2 = pd.Series({"given_name": "bnjmin", "surname": "haer"})
    assert not deduplicate._similar_fullname(patient_1, patient_2)


def _build_id_groups():
    id_pairs = [(1, 2), (2, 3), (8, 9)]
    expected_result = {1: {1, 2, 3}, 2: {1, 2, 3}, 3: {1, 2, 3}, 8: {8, 9}, 9: {8, 0}}
    assert deduplicate._build_id_groups(id_pairs) == expected_result
