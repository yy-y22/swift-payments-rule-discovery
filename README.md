# Swift Payment Rule Discovery

A Streamlit dashboard for exploring patterns in a fictitious cross-border payment dataset created for UM Datathon 2026.

The app presents seven analytical dashboards covering payment participants and values, routing and timing, currency conversion, account-format patterns, anomaly examples, and data preparation. It is an educational data-analysis project, not a live payment tracker, fraud detector, or financial advice service.

## Run the dashboard

The small summary files needed by the app are included in this repository.

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Run these commands from the project directory. Streamlit will print a local URL to open in your browser.

## Data files

The app reads these files from the project directory:

- `comp_party.csv`
- `comp_routing.csv`
- `comp_fx.csv`
- `comp_time.csv`
- `comp_token.csv`
- `comp_currency.csv`
- `swift_all_anomalies.csv`

The full source CSV is approximately 4.72 GB and is not included. The unused 20,000-row sample is also excluded. The summary and anomaly files included here are derived from fictitious payment data.

If you have authorized access to the full source dataset and want to rebuild the summaries, place it in this directory as `swift_umdac_datathon_2026_fictitious_payment_data.csv`, then run:

```powershell
python prepare_dashboard_data.py
python sample_data.py
```

These scripts process the source data in chunks and write the CSV files used by the dashboard. Processing may take time and require substantial disk space. Only redistribute source or derived data when its terms allow it.

## Important limitations

- The data is fictitious; observed patterns do not establish how a real bank or payment provider will process a transfer.
- An anomaly label or pattern in this dataset does not identify a real scam or person.
- No live exchange rates, payment status, recipient-account validation, or bank cut-off times are provided.

## License

No license is included yet. Check the rights to the code and data before reusing or redistributing them.
