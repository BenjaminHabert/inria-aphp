def merge_pcr_tests(patients, pcr):
    all_patient_ids = patients.loc[:, ["patient_id", "all_patient_ids"]].explode(
        "all_patient_ids"
    )
    pcr_to_merge = pcr.rename(columns={"patient_id": "all_patient_ids"})
    merged = pcr_to_merge.merge(all_patient_ids, on="all_patient_ids", how="left")
    one_result_per_patient = (
        merged.groupby("patient_id")["pcr_positive"].any().reset_index()
    )
    patients = patients.merge(one_result_per_patient, on="patient_id", how="left")
    return patients
