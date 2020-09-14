def detect_duplicates(df_patient):
    """Remove duplicates from Dataframe of patients

    Parameters
    ----------
        df_patient: DataFrame of patients
            - required columns: `['patient_id', 'given_name', 'surname', 'street_number',
                'address_1', 'suburb', 'postcode', 'state', 'age', 'phone_number', 'address_2',
                'birthday']`
            - can contain additional columns that will be preserved

    Returns
    -------
        DataFrame similar to input df_patient with:
            - duplicated_removed
            - additional column `all_patient_ids` containing a set of `patient_id`
              from the original dataframe

    """
    same_phone = _find_pairs_from_phone(df_patient)
    same_postcode = _find_pairs_from_postcode_and_birthday(df_patient)

    all_pairs_of_ids = same_phone + same_postcode
    df = _deduplicate(df_patient, all_pairs_of_ids)

    return df


def _find_pairs_from_phone(df_patient):
    pairs = []
    return pairs


def _find_pairs_from_postcode_and_birthday(df_patient):
    pairs = []
    return pairs


def _deduplicate(df_patient, pairs_of_ids):
    groups = _build_id_groups(pairs_of_ids)
    df_with_id_group = _add_id_groups(df_patient, groups)
    df_deduplicated = _keep_one_line_per_patient(df_with_id_group)
    return df_deduplicated


def _build_id_groups(pairs_of_ids):
    return {}


def _add_id_groups(df_patient, groups_of_ids):
    return df_patient


def _keep_one_line_per_patient(df_with_id_group):
    return df_with_id_group
