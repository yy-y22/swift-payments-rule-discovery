import pandas as pd

file_path = "swift_umdac_datathon_2026_fictitious_payment_data.csv"
anomalies = []

for chunk in pd.read_csv(file_path, chunksize=200_000, low_memory=False):
    flagged = chunk[chunk['ANOMALY_TYPE'].notna()]
    if not flagged.empty:
        anomalies.append(flagged)

df_anom = pd.concat(anomalies, ignore_index=True)
print("Total anomaly rows found:", len(df_anom))
print(df_anom['ANOMALY_TYPE'].value_counts())

# Drop raw detail text columns if uploading here
cols_to_drop = [c for c in ['ORDERING_DETAILS', 'BENEFICIARY_DETAILS'] if c in df_anom.columns]
df_anom.drop(columns=cols_to_drop).to_csv("swift_all_anomalies.csv", index=False)