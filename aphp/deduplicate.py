import logging
import time

import pandas as pd
import numpy as np
import Levenshtein

from aphp import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def runtime(func):
    def wrapped_func(*args, **kwargs):
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        eslapsed = time.perf_counter() - t0
        logger.info(f"<{func.__name__}> - {eslapsed:.1f} s")
        return result

    return wrapped_func


@runtime
def detect_duplicates(df_patient):
    """Remove duplicates from Dataframe of patients

    Parameters
    ----------
        df_patient: DataFrame of patients
            - required columns: `['patient_id', 'given_name', 'surname', 'postcode',
              'age', 'phone_number', 'birthday']`
            - can contain additional columns that will be preserved

    Returns
    -------
        DataFrame similar to input df_patient with:
            - duplicates removed
            - additional column `all_patient_ids` containing a set of `patient_id`
              from the original dataframe

    """
    same_phone = _find_pairs_from_phone(df_patient)
    same_postcode = _find_pairs_from_postcode_and_birthday(df_patient)
    all_pairs_of_ids = list(set(same_phone + same_postcode))

    logger.info(f"Found {len(same_phone)} pairs of duplicates using phone numbers.")
    logger.info(f"Found {len(same_postcode)} pairs of duplicates using birthday.")
    logger.info(f"Found {len(all_pairs_of_ids)} total pairs of duplicates.")

    df = _deduplicate(df_patient, all_pairs_of_ids)

    logger.info(f"Patient deduplication: {len(df_patient)} -> {len(df)}")

    return df


@runtime
def _find_pairs_from_phone(df_patient):
    """Return list of (patient_id_1, patient_id_2) for duplicated users.

    Patients are considered duplicates if they have the same phone and either:
        - similar fullename
        - or same birthday
        - or same given_name

    """
    pairs = []
    duplicate_candidates = _iter_patient_pairs_by_group(df_patient, "phone_number")

    for patient_1, patient_2 in duplicate_candidates:
        conditions = (
            _is_same(patient_1, patient_2, "birthday"),
            _is_same(patient_1, patient_2, "given_name"),
            _similar_fullname(patient_1, patient_2),
        )
        if any(conditions):
            pairs.append((patient_1["patient_id"], patient_2["patient_id"]))
    return pairs


@runtime
def _find_pairs_from_postcode_and_birthday(df_patient):
    pairs = []
    duplicate_candidates = _iter_patient_pairs_by_group(
        df_patient, ["postcode", "birthday"]
    )

    for patient_1, patient_2 in duplicate_candidates:
        conditions = (
            _is_same(patient_1, patient_2, "age")
            and _similar_fullname(patient_1, patient_2),
        )
        if any(conditions):
            pairs.append((patient_1["patient_id"], patient_2["patient_id"]))
    return pairs


@runtime
def _deduplicate(df_patient, pairs_of_ids):
    groups = _build_id_groups(pairs_of_ids)
    df_with_id_group = _add_id_groups(df_patient, groups)
    df_deduplicated = _keep_one_line_per_patient(df_with_id_group)
    return df_deduplicated


def _add_id_groups(df_patient, groups_of_ids):
    """Add `all_patient_ids` to df_patient.

    Parameters
    ----------
        df_patient: DataFrame, same as `detect_duplicates()`
        groups_of_ids: dict of sets; `patient_id -> {group_of_patient_ids}`

    Returns
    -------
        DataFrame with additional column: `all_patient_ids` (list)

    """
    starting_dtype = df_patient["patient_id"].dtype

    # build dataframe of patient_ids
    records = (
        {
            "patient_id": key,
            "all_patient_ids": list(
                sorted(value)
            ),  # sorted is just here to make sure the output is allways the same
            "unique_patient_id": min(value),
        }
        for key, value in groups_of_ids.items()
    )
    id_info = pd.DataFrame.from_records(records)
    df = df_patient.merge(id_info, on="patient_id", how="left")

    # if no match after merge (a line without duplicates), the list of all_patient_ids is just
    # this patient_id
    missing_id = df["all_patient_ids"].isnull()
    df.loc[missing_id, "all_patient_ids"] = df.loc[missing_id, "patient_id"].transform(
        lambda patient_id: [patient_id]
    )

    # otherwise (when it did match), we replace the patient_id by a unique_patient_id
    # patient_id will now show the actual duplicates
    df.loc[~missing_id, "patient_id"] = df.loc[~missing_id, "unique_patient_id"]
    df["patient_id"] = df["patient_id"].astype(starting_dtype)

    df = df.drop("unique_patient_id", axis="columns")
    return df


@runtime
def _keep_one_line_per_patient(df_with_id_group):
    """Remove duplicates of `patient_id` while keeping the most frequent data for each duplicate."""
    columns = df_with_id_group.columns

    def keep_most_frequent(df):
        if len(df) == 1:
            return df.iloc[0]
        s = {}
        for col in columns:
            values = df[col].value_counts()
            if values.empty:
                s[col] = np.NaN
            else:
                s[col] = values.index[0]

        return pd.Series(s)

    return df_with_id_group.groupby("patient_id", as_index=False).apply(
        keep_most_frequent
    )


# Utility functions


def _build_id_groups(pairs_of_ids):
    """Create dict of id groups (as sets) from list of id pairs

    Exemple
    -------

        >>> _build_id_groups([(1, 2), (2, 3), (8, 9)])
        {
            1: {1, 2, 3},
            2: {1, 2, 3},
            3: {1, 2, 3},
            8: {8, 9},
            9: {8, 0}
        }

    """
    groups = {}
    for (x, y) in pairs_of_ids:
        xset = groups.get(x, set([x]))
        yset = groups.get(y, set([y]))
        jset = xset | yset
        for z in jset:
            groups[z] = jset
    return groups


def _iter_patient_pairs_by_group(df_patient, groupby_condition):
    for _, group in df_patient.groupby(groupby_condition):
        if len(group) < 2:
            continue
        yield from _iter_pairs_of_rows(group)


def _iter_pairs_of_rows(df):
    for i, (_, row_1) in enumerate(df.iterrows()):
        for _, row_2 in df.iloc[i + 1 :].iterrows():  # noqa E203
            yield (row_1, row_2)


def _similar_fullname(
    patient_1, patient_2, maximum_distance=settings.DEDUPLICATION_MAX_LEVEN_DISTANCE
):
    # comparison is only allowed if we have both given_name and surname
    values = [
        p[col] for p in (patient_1, patient_2) for col in ("given_name", "surname")
    ]
    if any(v is None or v is np.NaN for v in values):
        return False

    fullname_1 = _sorted_string(patient_1["given_name"], patient_1["surname"])
    fullname_2 = _sorted_string(patient_2["given_name"], patient_2["surname"])
    return Levenshtein.distance(fullname_1, fullname_2) <= maximum_distance


def _sorted_string(*string_elements):
    without_nans = (s if s and s is not np.NaN else "" for s in string_elements)
    assembled = " ".join(without_nans)
    return " ".join(sorted(s for s in assembled.split(" "))).strip()


def _is_same(patient_1, patient_2, column):
    return (
        patient_1[column] is not None
        and patient_1[column] is not np.NaN
        and patient_1[column] == patient_2[column]
    )
