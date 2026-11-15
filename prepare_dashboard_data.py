import pandas as pd

file_path = "swift_umdac_datathon_2026_fictitious_payment_data.csv"

g_party, g_routing, g_fx, g_time, g_token, g_curr = [], [], [], [], [], []

print("Running full 10M competition rule extraction...")
for i, chunk in enumerate(pd.read_csv(file_path, chunksize=500_000, low_memory=False)):
    # 1. Party & Amount rules
    g_party.append(chunk.groupby(['ORDERING_TYPE', 'BENEFICIARY_TYPE']).agg(
        tx_count=('USD_AMOUNT', 'count'),
        total_usd=('USD_AMOUNT', 'sum'),
        median_usd=('USD_AMOUNT', 'median')
    ).reset_index())

    # 2. Routing & Latency rules
    g_routing.append(chunk.groupby(['TRANSACTION_TYPE_CODE', 'CONTINUITY_QFLAG', 'PARTICIPANT_COUNT']).agg(
        tx_count=('USD_AMOUNT', 'count'),
        median_duration=('TOTAL_DURATION', 'median'),
        mean_duration=('TOTAL_DURATION', 'mean')
    ).reset_index())

    # 3. FX Conversion & Hop Bounds
    chunk['ord_cc'] = chunk['ORDERING_BIC8'].str[4:6]
    chunk['ben_cc'] = chunk['BENEFICIARY_BIC8'].str[4:6]
    chunk['cross_border'] = chunk['ord_cc'] != chunk['ben_cc']
    g_fx.append(chunk.groupby(['PARTICIPANT_COUNT', 'CURRENCY_CONVERSION_COUNT', 'cross_border']).agg(
        tx_count=('USD_AMOUNT', 'count')
    ).reset_index())

    # 4. Temporal & Weekend Clearing rules
    dt = pd.to_datetime(chunk['EPOCH_SECONDS'], unit='s')
    chunk['hour_utc'] = dt.dt.hour
    chunk['dow'] = dt.dt.dayofweek
    g_time.append(chunk.groupby(['dow', 'hour_utc', 'ORDERING_TYPE']).agg(
        tx_count=('USD_AMOUNT', 'count'),
        total_usd=('USD_AMOUNT', 'sum')
    ).reset_index())

    # 5. Token & IBAN Jurisdiction rules
    chunk['ord_has_iban'] = chunk['ORDERING_TOKENS'].str.contains('<iban:', na=False)
    g_token.append(chunk.groupby(['ord_cc', 'ORDERING_TYPE', 'ord_has_iban']).agg(
        tx_count=('USD_AMOUNT', 'count')
    ).reset_index())

    # 6. Currency dominance
    g_curr.append(chunk.groupby(['CURRENCY_CODE', 'ORDERING_TYPE']).agg(
        tx_count=('USD_AMOUNT', 'count'),
        total_usd=('USD_AMOUNT', 'sum')
    ).reset_index())

    print(f"Processed {(i + 1) * 500_000:,} / 10,000,000 rows...")

pd.concat(g_party).groupby(['ORDERING_TYPE', 'BENEFICIARY_TYPE'], as_index=False).agg(
    tx_count=('tx_count', 'sum'), total_usd=('total_usd', 'sum'), median_usd=('median_usd', 'median')
).to_csv("comp_party.csv", index=False)

pd.concat(g_routing).groupby(['TRANSACTION_TYPE_CODE', 'CONTINUITY_QFLAG', 'PARTICIPANT_COUNT'], as_index=False).agg(
    tx_count=('tx_count', 'sum'), median_duration=('median_duration', 'median'), mean_duration=('mean_duration', 'mean')
).to_csv("comp_routing.csv", index=False)

pd.concat(g_fx).groupby(['PARTICIPANT_COUNT', 'CURRENCY_CONVERSION_COUNT', 'cross_border'], as_index=False).agg(
    tx_count=('tx_count', 'sum')
).to_csv("comp_fx.csv", index=False)

pd.concat(g_time).groupby(['dow', 'hour_utc', 'ORDERING_TYPE'], as_index=False).agg(
    tx_count=('tx_count', 'sum'), total_usd=('total_usd', 'sum')
).to_csv("comp_time.csv", index=False)

pd.concat(g_token).groupby(['ord_cc', 'ORDERING_TYPE', 'ord_has_iban'], as_index=False).agg(
    tx_count=('tx_count', 'sum')
).to_csv("comp_token.csv", index=False)

pd.concat(g_curr).groupby(['CURRENCY_CODE', 'ORDERING_TYPE'], as_index=False).agg(
    tx_count=('tx_count', 'sum'), total_usd=('total_usd', 'sum')
).to_csv("comp_currency.csv", index=False)

print("All 6 competition aggregation tables saved!")