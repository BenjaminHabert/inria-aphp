import pandas as pd
from numpy import NaN


def clean_raw_patient_data(df):
    df = _remove_duplicate_id(df)
    df = _extract_birthday(df)
    df = _clean_state(df)
    df = _clean_postcode(df)
    df = _clean_phone(df)
    return df


def _remove_duplicate_id(df):
    df.drop_duplicates(subset=["patient_id"], keep=False, inplace=True)
    return df


def _extract_birthday(df):
    dates = pd.to_datetime(
        df["date_of_birth"].astype(str), format="%Y%m%d.0", errors="coerce"
    )
    birthdays = dates.dt.strftime(date_format="%m-%d")

    df["birthday"] = birthdays
    df = df.drop("date_of_birth", axis=1)

    return df


def _clean_state(df):
    states = {
        "nsw": "New South Wales",
        "vic": "Victoria",
        "qld": "Queensland",
        "wa": "Western Australia",
        "sa": "South Australia",
        "tas": "Tasmania",
        "act": "Australian Capital Territory",
        "nt": "Northern Territory",
    }
    df["state"] = df["state"].map(states)
    return df


def _clean_postcode(df):
    valid_postcode = df["postcode"].str.match(r"\d{4}").fillna(value=False)
    df.loc[~valid_postcode, "postcode"] = NaN

    # sometimes the postcode is in the suburb column
    postcode_in_suburb = df["suburb"].str.match(r"\d{4}") & df["postcode"].isnull()
    df.loc[postcode_in_suburb, "postcode"] = df.loc[postcode_in_suburb, "suburb"]

    return df


def _clean_phone(df):
    valid_phone = df["phone_number"].str.match(r"\d{2} \d{8}").fillna(value=False)
    df.loc[~valid_phone, "phone_number"] = NaN
    return df
