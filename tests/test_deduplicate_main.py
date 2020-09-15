import pandas as pd
import numpy as np

from aphp import deduplicate


def test_find_pairs_from_phone():
    df = pd.DataFrame(
        data=[
            ("A", "benjamin", "habert", "phone_number_1", None),
            ("B", "bnjamin", "habrt", "phone_number_1", None),  # same as A
            ("C", "benjamin", None, "phone_number_1", None),  # same as A
            ("D", "benja", None, "phone_number_1", None),
            ("E", "benjamin", "habert", "phone_number_2", None),
        ],
        columns=["patient_id", "given_name", "surname", "phone_number", "birthday"],
    )
    result = list(deduplicate._find_pairs_from_phone(df))
    assert result == [("A", "B"), ("A", "C")]

    df = pd.DataFrame(
        data=[
            ("A", "benjamin", "habert", "phone_number_1", "05-12"),
            ("B", None, None, "phone_number_1", "05-12"),  # same as A
            ("D", None, None, "phone_number_1", None),
            ("E", "benjamin", "habert", "phone_number_2", "05-12"),
        ],
        columns=["patient_id", "given_name", "surname", "phone_number", "birthday"],
    )
    result = list(deduplicate._find_pairs_from_phone(df))
    assert result == [("A", "B")]


def test_add_id_groups():
    df = pd.DataFrame(
        data=[
            ("A", "benjamin"),
            ("B", "habert"),
            ("C", "other"),
        ],
        columns=["patient_id", "some_column"],
    )
    groups_of_ids = {"A": {"A", "B"}, "B": {"A", "B"}}
    expected_result = pd.DataFrame(
        data=[
            ("A", "benjamin", ["A", "B"]),
            ("A", "habert", ["A", "B"]),
            ("C", "other", ["C"]),
        ],
        columns=["patient_id", "some_column", "all_patient_ids"],
    )
    result = deduplicate._add_id_groups(df, groups_of_ids)

    pd.testing.assert_frame_equal(result, expected_result)


def test_keep_one_line_per_patient():
    df = pd.DataFrame(
        data=[
            ("A", "bjamin", np.NaN, ["A", "B"]),
            ("A", "benjamin", np.NaN, ["A", "B"]),
            ("A", "benjamin", "test", ["A", "B"]),
            ("C", "other", np.NaN, ["C"]),
        ],
        columns=["patient_id", "name", "col_with_nan", "all_patient_ids"],
    )
    expected_result = pd.DataFrame(
        data=[
            ("A", "benjamin", "test", ["A", "B"]),
            ("C", "other", np.NaN, ["C"]),
        ],
        columns=["patient_id", "name", "col_with_nan", "all_patient_ids"],
    )
    result = deduplicate._keep_one_line_per_patient(df)
    print(result)
    pd.testing.assert_frame_equal(result, expected_result)
