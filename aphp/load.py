import pandas as pd
from sqlalchemy import create_engine

from aphp import settings, clean_patient


def load_clean_patients():
    df = load_raw_patients()
    return clean_patient.clean_raw_patient_data(df)


def load_raw_patients():
    return load_table_from_sqlite("patient")


def load_raw_tests():
    return load_table_from_sqlite("test")


def load_table_from_sqlite(table, sqlite_abspath=settings.SQLITE_ABSPATH):
    engine = create_engine(f"sqlite:///{sqlite_abspath}", echo=False)
    with engine.connect() as connexion:
        df = pd.read_sql(f"select * from {table}", con=connexion)
    return df
