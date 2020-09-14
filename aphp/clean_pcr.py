def clean_raw_pcr(df):
    df["pcr_positive"] = df["pcr"].str.capitalize().str.slice(0, 1) == "P"
    df = df.groupby("patient_id")["pcr_positive"].any().reset_index()
    return df
