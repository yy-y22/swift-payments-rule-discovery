import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Swift Payments | Reconstructed Business Rules", layout="wide")

# Unified Semantic Color Palette (Consistent across all 7 dashboards)
ENTITY_COLORS = {
    "B": "#1E3A8A", "C": "#0D9488",
    "B → B": "#1E3A8A", "B → C": "#2563EB",
    "C → B": "#0D9488", "C → C": "#14B8A6"
}
ROUTE_COLORS = {
    "Direct": "#2563EB",
    "Indirect": "#F59E0B",
    "Covered": "#DC2626"
}
ANOM_COLORS = {
    "ROMANCE_SCAM": "#E11D48",
    "FAT_FINGER_MISTAKE": "#D97706",
    "CEO_SCAM": "#7C3AED",
    "DUPLICATE_PAYMENT": "#2563EB",
    "ACCOUNT_REPLACEMENT_SCAM": "#059669",
    "CUSTOMER_RECALL": "#64748B"
}

PLOT_CONFIG = {"displayModeBar": False}

st.markdown("""
<style>
@media print {
    [data-testid="stSidebar"], .no-print { display: none !important; }
    .page-break { page-break-after: always; break-after: page; }
    .block-container { padding-top: 0.5rem !important; max-width: 100% !important; }
}
.rule-box {
    background-color: #EFF6FF;
    border-left: 5px solid #1E3A8A;
    padding: 10px 14px;
    border-radius: 4px;
    margin-bottom: 10px;
    color: #0F172A;
    font-size: 0.92rem;
}
.econ-box {
    background-color: #F0FDF4;
    border-left: 5px solid #059669;
    padding: 9px 14px;
    border-radius: 4px;
    margin-top: 6px;
    margin-bottom: 12px;
    color: #0F172A;
    font-size: 0.89rem;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_all():
    party = pd.read_csv("comp_party.csv")
    routing = pd.read_csv("comp_routing.csv")
    fx = pd.read_csv("comp_fx.csv")
    time_df = pd.read_csv("comp_time.csv")
    token = pd.read_csv("comp_token.csv")
    curr = pd.read_csv("comp_currency.csv")
    anom = pd.read_csv("swift_all_anomalies.csv")
    return party, routing, fx, time_df, token, curr, anom

party, routing, fx, time_df, token, curr, anom = load_all()

st.sidebar.title("UMDAC Datathon 2026")
st.sidebar.caption("Swift Cross-Border Payments (10,000,000 Records)")
view_mode = st.sidebar.radio(
    "Select Dashboard View:",
    [
        "All 7 Dashboards (PDF Export View)",
        "Dashboard 1: Party & Value Tiers",
        "Dashboard 2: Routing & Latency Confounders",
        "Dashboard 3: FX Conversion Hop Bounds",
        "Dashboard 4: Temporal & Weekend Clearing",
        "Dashboard 5: Jurisdiction, IBAN & Home Currency",
        "Dashboard 6: Anomaly Graphs & Mule Hubs",
        "Dashboard 7: Priority Matrix, Data Log & Compliance"
    ]
)
st.sidebar.info("PDF Export: Select 'All 7 Dashboards' → click ⋮ (top-right) → Print → Save as PDF (Landscape, Background Graphics ON).")

def style_fig(fig, height=340):
    fig.update_layout(
        height=height,
        margin=dict(t=55, b=30, l=45, r=20),
        plot_bgcolor="white",
        paper_bgcolor="white",
        title_font_size=13,
        font=dict(size=11, color="#1E293B")
    )
    fig.update_xaxes(showgrid=False, linecolor="#CBD5E1")
    fig.update_yaxes(gridcolor="#F1F5F9", linecolor="#CBD5E1", automargin=True)
    return fig

def show_header_kpis():
    total_tx = int(party['tx_count'].sum())
    total_vol = party['total_usd'].sum()
    st.title("Swift Cross-Border Payments: Reconstructed Business Rules")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Dataset Scope", f"{total_tx:,} txns", "100% Full-Scan Verified")
    k2.metric("Total Volume (USD)", f"${total_vol/1e9:,.2f}B", "Median: $3,586 / txn")
    k3.metric("Deterministic Laws", "4 Exact Rules", "0 Exceptions Across 10M")
    k4.metric("Labeled Anomalies", f"{len(anom):,} (0.070%)", "6 Distinct Graph Motifs")
    st.divider()

def show_d1():
    st.subheader("Dashboard 1: Party Roles & Payment Value Tiers")
    st.markdown("""
    <div class="rule-box">
    <b>Reconstructed Rule 1 (Priority Tier 1 — Scope: 100% of 10,000,000 records):</b> Ordering/Beneficiary entity type (<code>B</code> = Business, <code>C</code> = Consumer) governs both volume share and value tier.
    <code>B → B</code> transfers carry a median value <b>~43× larger</b> than the <code>C → C</code> baseline ($21.2K vs. $488), while <code>B → C</code> accounts for <b>~56%</b> of total transactions.
    </div>
    """, unsafe_allow_html=True)

    p = party.copy()
    p['Pair'] = p['ORDERING_TYPE'] + " → " + p['BENEFICIARY_TYPE']
    p = p.sort_values('tx_count', ascending=False)
    p['Share (%)'] = (p['tx_count'] / p['tx_count'].sum() * 100).round(1)

    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.bar(p, x='Pair', y='tx_count', text='Share (%)', color='Pair', color_discrete_map=ENTITY_COLORS,
                      title="B→C Dominates Volume (~56%), While C→B Is Least Frequent (~6.4%)",
                      labels={'tx_count': 'Transactions (10M)', 'Pair': 'Party Pair'})
        fig1.update_traces(texttemplate='%{text}%', textposition='outside')
        fig1.update_yaxes(range=[0, p['tx_count'].max() * 1.18])
        fig1.update_layout(showlegend=False)
        st.plotly_chart(style_fig(fig1), use_container_width=True, config=PLOT_CONFIG)
    with c2:
        p_med = p.sort_values('median_usd', ascending=False)
        fig2 = px.bar(p_med, x='Pair', y='median_usd', text='median_usd', color='Pair', color_discrete_map=ENTITY_COLORS,
                      title="B→B Median Value ($21.2K) Is 43× Higher Than C→C Baseline ($488)",
                      labels={'median_usd': 'Median Amount (USD)', 'Pair': 'Party Pair'})
        fig2.add_hline(y=3586, line_dash="dash", line_color="#64748B",
                       annotation_text="Dataset Baseline Median ($3,586)", annotation_position="top right")
        fig2.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig2.update_yaxes(range=[0, p_med['median_usd'].max() * 1.22])
        fig2.update_layout(showlegend=False)
        st.plotly_chart(style_fig(fig2), use_container_width=True, config=PLOT_CONFIG)

    st.markdown("""
    <div class="econ-box">
    <b>Observed vs. Real-World Economic Mechanism:</b> <i>Observed:</i> B→C leads frequency while B→B leads median size. <i>Interpretation:</i> B→C captures high-frequency cross-border payroll, contractor payouts, and insurance disbursements, whereas B→B reflects bulk commercial invoice settlement.
    </div><div class="page-break"></div>
    """, unsafe_allow_html=True)

def show_d2():
    st.subheader("Dashboard 2: Routing Topology & Confounder-Controlled Latency")
    st.markdown("""
    <div class="rule-box">
    <b>Reconstructed Rule 2 (Priority Tier 1 — Scope: 100% of 10,000,000 records):</b> <code>TRANSACTION_TYPE_CODE == "Direct"</code> holds <b>iff</b> <code>PARTICIPANT_COUNT == 2</code> (100% exact). Controlling for hop count reveals two causal latency drivers: (1) each added intermediary adds <b>~150s–250s</b>, and (2) at 3 banks, <code>Covered</code> (~346s) is <b>3.9× slower</b> than <code>Indirect</code> (~89s). <code>CONTINUITY_QFLAG == "N"</code> occurs <b>iff</b> <code>BIC8_PATH</code> contains <code>...</code> (~7.65%).
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        hop_agg = routing.groupby(['PARTICIPANT_COUNT', 'TRANSACTION_TYPE_CODE'], as_index=False)['tx_count'].sum()
        fig1 = px.bar(hop_agg, x='PARTICIPANT_COUNT', y='tx_count', color='TRANSACTION_TYPE_CODE',
                      color_discrete_map=ROUTE_COLORS, barmode='group',
                      title="Direct Routing Occurs Exclusively at 2 Banks; 3+ Banks Split Indirect vs. Covered",
                      labels={'PARTICIPANT_COUNT': 'Bank Participants in BIC8_PATH', 'tx_count': 'Transactions'})
        st.plotly_chart(style_fig(fig1), use_container_width=True, config=PLOT_CONFIG)
    with c2:
        hop_lat = routing[routing['PARTICIPANT_COUNT'] <= 8].groupby(
            ['PARTICIPANT_COUNT', 'TRANSACTION_TYPE_CODE'], as_index=False
        )['median_duration'].median()
        fig2 = px.line(hop_lat, x='PARTICIPANT_COUNT', y='median_duration', color='TRANSACTION_TYPE_CODE',
                       color_discrete_map=ROUTE_COLORS, markers=True,
                       title="Confounder Control: Latency Scales Linearly With Hop Count (+150–250s/Hop)",
                       labels={'PARTICIPANT_COUNT': 'Bank Participants (Hops + 1)', 'median_duration': 'Median Duration (Sec)'})
        fig2.add_hline(y=40, line_dash="dash", line_color="#64748B",
                       annotation_text="2-Bank Direct Baseline (40s)", annotation_position="bottom right")
        st.plotly_chart(style_fig(fig2), use_container_width=True, config=PLOT_CONFIG)

    st.markdown("""
    <div class="econ-box">
    <b>Observed vs. Real-World Economic Mechanism:</b> <i>Observed:</i> Controlling for participant count shows Covered routes carry a fixed overhead penalty at 3 banks before hop count dominates. <i>Interpretation:</i> Cover payments decouple the customer message (MT103) from bank-to-bank cover settlement (MT202), creating bilateral reconciliation latency even on short chains.
    </div><div class="page-break"></div>
    """, unsafe_allow_html=True)

def show_d3():
    st.subheader("Dashboard 3: Foreign Exchange (FX) Conversion Hop Bounds")
    st.markdown("""
    <div class="rule-box">
    <b>Reconstructed Rule 3 (Priority Tier 1 — Scope: 100% of 10,000,000 records):</b> Across all 10 million records, <code>CURRENCY_CONVERSION_COUNT ≤ PARTICIPANT_COUNT - 1</code> holds with <b>zero exceptions</b> (at most 1 FX conversion per interbank edge). Cross-border BIC routes trigger ≥1 FX conversion <b>~93%</b> of the time vs. <b>~35%</b> for same-country BIC routes.
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        fx_mat = fx.groupby(['PARTICIPANT_COUNT', 'CURRENCY_CONVERSION_COUNT'], as_index=False)['tx_count'].sum()
        piv = fx_mat.pivot(index='PARTICIPANT_COUNT', columns='CURRENCY_CONVERSION_COUNT', values='tx_count').fillna(0)
        fig1 = px.imshow(np.log10(piv + 1), text_auto='.1f', aspect='auto', color_continuous_scale='Blues',
                         title="Strict Triangular Law: FX Conversions Never Exceed (Participants - 1) [Log10 Txns]",
                         labels={'x': 'CURRENCY_CONVERSION_COUNT', 'y': 'PARTICIPANT_COUNT', 'color': 'Log10(Txns)'})
        st.plotly_chart(style_fig(fig1), use_container_width=True, config=PLOT_CONFIG)
    with c2:
        cb = fx.copy()
        cb['Has_FX'] = np.where(cb['CURRENCY_CONVERSION_COUNT'] > 0, '≥1 FX Conversion', '0 FX Conversions')
        cb['Route'] = np.where(cb['cross_border'], 'Cross-Border BICs', 'Same-Country BICs')
        cb_agg = cb.groupby(['Route', 'Has_FX'], as_index=False)['tx_count'].sum()
        cb_agg['Pct'] = (cb_agg['tx_count'] / cb_agg.groupby('Route')['tx_count'].transform('sum') * 100).round(1)
        fig2 = px.bar(cb_agg, x='Route', y='Pct', color='Has_FX', text='Pct',
                      color_discrete_map={'≥1 FX Conversion': '#1E3A8A', '0 FX Conversions': '#94A3B8'},
                      title="Cross-Border BICs Require FX Conversion ~93% of the Time vs. ~35% Domestic",
                      labels={'Pct': 'Share of Route Volume (%)', 'Route': 'BIC8 Country Comparison'})
        fig2.update_traces(texttemplate='%{text}%', textposition='inside')
        st.plotly_chart(style_fig(fig2), use_container_width=True, config=PLOT_CONFIG)

    st.markdown("""
    <div class="econ-box">
    <b>Observed vs. Real-World Economic Mechanism:</b> <i>Observed:</i> Every cell above the diagonal (FX &gt; Participants − 1) is strictly zero. <i>Interpretation:</i> An institution converts currency only when settling across an interbank leg; a single bank cannot execute multiple sequential FX steps on one hop without routing through an additional correspondent.
    </div><div class="page-break"></div>
    """, unsafe_allow_html=True)

def show_d4():
    st.subheader("Dashboard 4: Temporal Activity & Weekend Clearing Closures")
    st.markdown("""
    <div class="rule-box">
    <b>Reconstructed Rule 4 (Priority Tier 2 — Scope: 100% of 10,000,000 records):</b> Daily volume remains flat Monday–Friday (~17–19% per weekday), then plunges by <b>~77% on Saturday</b> and <b>~62% on Sunday</b> across both Businesses and Consumers. Normalizing timestamps to sender local time shows <b>~57%</b> of daytime volume occurs during local banking hours (<code>08:00–17:00</code>).
    </div>
    """, unsafe_allow_html=True)

    day_names = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
    t = time_df.copy()
    t['Day'] = t['dow'].map(day_names)
    c1, c2 = st.columns(2)
    with c1:
        dow_agg = t.groupby(['dow', 'Day', 'ORDERING_TYPE'], as_index=False)['tx_count'].sum().sort_values('dow')
        fig1 = px.bar(dow_agg, x='Day', y='tx_count', color='ORDERING_TYPE', color_discrete_map=ENTITY_COLORS, barmode='group',
                      title="Weekend Settlement Drop: Saturday Volume Falls ~77% Below Weekday Baseline",
                      labels={'tx_count': 'Transactions', 'Day': 'Day of Week (UTC)'})
        st.plotly_chart(style_fig(fig1), use_container_width=True, config=PLOT_CONFIG)
    with c2:
        hr_agg = t.groupby(['hour_utc', 'ORDERING_TYPE'], as_index=False)['tx_count'].sum()
        fig2 = px.line(hr_agg, x='hour_utc', y='tx_count', color='ORDERING_TYPE', color_discrete_map=ENTITY_COLORS, markers=True,
                       title="Intraday UTC Cycle: Business Traffic Tracks Global Clearing Windows",
                       labels={'hour_utc': 'Hour of Day (UTC)', 'tx_count': 'Transactions'})
        st.plotly_chart(style_fig(fig2), use_container_width=True, config=PLOT_CONFIG)

    st.markdown("""
    <div class="econ-box">
    <b>Observed vs. Real-World Economic Mechanism:</b> <i>Observed:</i> Weekend volume collapses sharply and begins recovering late Sunday UTC (Monday morning in Asia-Pacific). <i>Interpretation:</i> High-value RTGS and correspondent clearing rails close on weekends, reopening first in Tokyo/Singapore/Sydney (~22:00–00:00 UTC Sunday).
    </div><div class="page-break"></div>
    """, unsafe_allow_html=True)

def show_d5():
    st.subheader("Dashboard 5: Jurisdiction Encoding, IBAN Tokens & Home-Currency Rule")
    st.markdown("""
    <div class="rule-box">
    <b>Reconstructed Rule 5 (Priority Tier 2 — Scope: 100% of 10,000,000 records):</b> Characters 5–6 of synthetic BIC8 codes encode ISO-2 country codes. Two jurisdiction rules govern formats: (1) <code>&lt;iban:&gt;</code> tokens appear at <b>~95–100%</b> in SEPA/European countries vs. <b>~0%</b> in US/SG/CN; (2) <b>90.0%</b> of payments are denominated in the <b>ordering (sender) country's home currency</b> (vs. 28.4% beneficiary currency and 5.4% third-party vehicle currencies).
    </div>
    """, unsafe_allow_html=True)

    top_cc = token.groupby('ord_cc', as_index=False)['tx_count'].sum().sort_values('tx_count', ascending=False).head(12)['ord_cc']
    sub_tok = token[token['ord_cc'].isin(top_cc)].groupby(['ord_cc', 'ord_has_iban'], as_index=False)['tx_count'].sum()
    tot_cc = sub_tok.groupby('ord_cc')['tx_count'].transform('sum')
    sub_tok['IBAN_Share (%)'] = (sub_tok['tx_count'] / tot_cc * 100).round(1)
    iban_only = sub_tok[sub_tok['ord_has_iban']].sort_values('IBAN_Share (%)', ascending=False)

    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.bar(iban_only, x='ord_cc', y='IBAN_Share (%)', text='IBAN_Share (%)',
                      color_discrete_sequence=['#1E3A8A'],
                      title="IBAN Token Usage Splits Sharply by BIC Country (SEPA ~100% vs. US/SG/CN ~0%)",
                      labels={'ord_cc': 'Ordering Country (BIC8[4:6])'})
        fig1.update_traces(texttemplate='%{text}%', textposition='outside')
        fig1.update_yaxes(range=[0, 118])
        st.plotly_chart(style_fig(fig1), use_container_width=True, config=PLOT_CONFIG)
    with c2:
        curr_rule_df = pd.DataFrame([
            {"Currency Match": "Matches Sender Home Currency", "Share (%)": 90.0},
            {"Currency Match": "Matches Receiver Home Currency", "Share (%)": 28.4},
            {"Currency Match": "Third-Party Vehicle (USD/EUR)", "Share (%)": 5.4}
        ])
        fig2 = px.bar(curr_rule_df, x='Currency Match', y='Share (%)', text='Share (%)',
                      color_discrete_sequence=['#0D9488'],
                      title="90.0% of Payment Instructions Use the Ordering Country's Home Currency",
                      labels={'Currency Match': 'Currency vs. BIC Country Rule'})
        fig2.update_traces(texttemplate='%{text}%', textposition='outside')
        fig2.update_yaxes(range=[0, 108])
        st.plotly_chart(style_fig(fig2), use_container_width=True, config=PLOT_CONFIG)

    st.markdown("""
    <div class="econ-box">
    <b>Observed vs. Real-World Economic Mechanism:</b> <i>Observed:</i> European BICs emit IBANs while US/APAC BICs emit non-IBAN strings, and 90% of instructions originate in sender currency. <i>Interpretation:</i> Reflects ISO 13616 IBAN adoption in SEPA zones and cross-border payment initiation where senders debit home-currency accounts and rely on correspondent FX conversion downstream.
    </div><div class="page-break"></div>
    """, unsafe_allow_html=True)

def show_d6():
    st.subheader("Dashboard 6: Anomaly Sequence Trajectories & Money-Mule Star Hubs")
    st.markdown("""
    <div class="rule-box">
    <b>Reconstructed Rule 6 (Priority Tier 3 — Scope: All 7,006 anomalies = 0.070% of 10M records):</b>
    (1) <b>1-to-1 Burst Chains:</b> <code>ROMANCE_SCAM</code> (2,476 rows, 100% <code>C→*</code>) compounds geometrically by <b>~1.50× per step</b> (1.0× → 1.5× → 2.3× → 3.5× → 5.2×), whereas <code>DUPLICATE_PAYMENT</code> (679 rows) replays the <b>exact same amount (1.00×)</b> within ~18 min;
    (2) <b>Many-to-1 Mule Hubs:</b> <code>CEO_SCAM</code> (945 rows, 100% <code>B→*</code>) and <code>ACCOUNT_REPLACEMENT_SCAM</code> (649 rows) funnel up to <b>13 distinct victims</b> into shared mule accounts;
    (3) <b>Single-Row Outliers:</b> <code>FAT_FINGER_MISTAKE</code> (1,940 rows, median $260.2K = 72× normal) and <code>CUSTOMER_RECALL</code> (317 rows).
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        traj_list = []
        for atype in ['ROMANCE_SCAM', 'DUPLICATE_PAYMENT']:
            sub = anom[anom['ANOMALY_TYPE'] == atype].sort_values(['ORDERING_ACCOUNT', 'BENEFICIARY_ACCOUNT', 'EPOCH_SECONDS']).copy()
            sub['Step'] = sub.groupby(['ORDERING_ACCOUNT', 'BENEFICIARY_ACCOUNT']).cumcount() + 1
            sub['First_Amt'] = sub.groupby(['ORDERING_ACCOUNT', 'BENEFICIARY_ACCOUNT'])['USD_AMOUNT'].transform('first')
            sub['Multiplier'] = sub['USD_AMOUNT'] / sub['First_Amt']
            agg_t = sub[sub['Step'] <= 5].groupby('Step', as_index=False)['Multiplier'].median()
            agg_t['ANOMALY_TYPE'] = atype
            traj_list.append(agg_t)
        traj_df = pd.concat(traj_list)
        fig1 = px.line(traj_df, x='Step', y='Multiplier', color='ANOMALY_TYPE', color_discrete_map=ANOM_COLORS, markers=True,
                       title="1-to-1 Burst Rule: Romance Scams Escalate ~1.5×/Step vs. Flat 1.0× Duplicate Replays",
                       labels={'Step': 'Transfer Sequence # (Same Pair)', 'Multiplier': 'Median Multiplier (vs. 1st Txn)'})
        st.plotly_chart(style_fig(fig1), use_container_width=True, config=PLOT_CONFIG)
    with c2:
        mule_df = anom[anom['ANOMALY_TYPE'].isin(['CEO_SCAM', 'ACCOUNT_REPLACEMENT_SCAM'])]
        top_mules = mule_df.groupby(['BENEFICIARY_ACCOUNT', 'ANOMALY_TYPE'], as_index=False).agg(
            Victims=('ORDERING_ACCOUNT', 'nunique')
        )
        # Rank accounts by total combined victims first so stacked bars fit cleanly
        acct_order = top_mules.groupby('BENEFICIARY_ACCOUNT')['Victims'].sum().nlargest(7).index
        top_mules = top_mules[top_mules['BENEFICIARY_ACCOUNT'].isin(acct_order)]
        top_mules['Short_Acct'] = top_mules['BENEFICIARY_ACCOUNT'].str.replace('_FAKE_', '', regex=False).str[:14]
        fig2 = px.bar(top_mules, x='Victims', y='Short_Acct', color='ANOMALY_TYPE', color_discrete_map=ANOM_COLORS,
                      orientation='h', text='Victims', category_orders={'Short_Acct': [a.replace('_FAKE_', '')[:14] for a in acct_order]},
                      title="Many-to-1 Mule Topology: Top Beneficiary Hubs Collect From 7–22 Victims",
                      labels={'Victims': 'Distinct Victim Accounts', 'Short_Acct': 'Beneficiary Mule Account'})
        fig2.update_traces(textposition='inside')
        fig2.update_xaxes(range=[0, 25])
        fig2.update_yaxes(autorange='reversed')
        st.plotly_chart(style_fig(fig2), use_container_width=True, config=PLOT_CONFIG)

    st.markdown("""
    <div class="econ-box">
    <b>Observed vs. Real-World Economic Mechanism:</b> <i>Observed:</i> Romance scams escalate geometrically from small initial tests ($109 median), while CEO/Account-Replacement scams converge multiple victims onto shared mule hubs. <i>Interpretation:</i> Romance fraudsters build victim trust before escalating demands; BEC/invoice-hijack syndicates route stolen corporate wires through shared money-mule accounts for rapid cash-out.
    </div>
    """, unsafe_allow_html=True)

    # Interactive sequence inspector (automatically hidden during PDF printing)
    with st.expander("Interactive Raw Anomaly Sequence Inspector (Hidden in PDF Print)", expanded=False):
        sel_anom = st.selectbox("Inspect Sample Rows for Anomaly Class:", anom['ANOMALY_TYPE'].unique())
        st.dataframe(
            anom[anom['ANOMALY_TYPE'] == sel_anom][
                ['EPOCH_SECONDS', 'CURRENCY_CODE', 'USD_AMOUNT', 'ORDERING_TYPE', 'BENEFICIARY_TYPE',
                 'ORDERING_ACCOUNT', 'BENEFICIARY_ACCOUNT', 'TOTAL_DURATION']
            ].head(15),
            use_container_width=True
        )
    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)

def show_d7():
    st.subheader("Dashboard 7: Rule Prioritization Matrix, Data Log & Governance")
    st.markdown("""
    <div class="rule-box">
    <b>Rubric 1.3 & 2.3 Scientific Rigor — Rule Prioritization, Rejected Hypothesis & Unexplained Residual Variance:</b><br>
    • <b>Rejected Hypothesis:</b> Businesses (<code>B</code>) use structured IBANs more often than Consumers (<code>C</code>). Full-dataset testing <b>rejected</b> this (<code>49.5% B</code> vs. <code>54.3% C</code>), isolating <b>country jurisdiction</b> as the true causal driver.<br>
    • <b>Unexplained Variance Disclosure:</b> While 90.0% of transactions use the sender's home currency, the remaining ~10% currency choice and isolated <code>CUSTOMER_RECALL</code> events (317 rows) do not follow a deterministic rule from observable features alone.
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**1. Reconstructed Rules Ranked by Impact & Coverage (Rubric 2.3)**")
        prio_df = pd.DataFrame([
            {"Priority": "Tier 1 (Exact)", "Rule Summary": "Direct ↔ 2 Participants; FX ≤ Participants − 1; Gap ('...') ↔ Flag 'N'", "Coverage": "100% (10.0M)"},
            {"Priority": "Tier 1 (Structural)", "Rule Summary": "B→B median ($21.2K) = 43× C→C ($488); B→C = 56% of volume", "Coverage": "100% (10.0M)"},
            {"Priority": "Tier 2 (Causal)", "Rule Summary": "Hop-count latency (+150–250s/hop) + Covered 3-bank overhead (3.9×)", "Coverage": "100% (10.0M)"},
            {"Priority": "Tier 2 (Behavioral)", "Rule Summary": "Weekend drop (−77% Sat); Sender currency (90%); SEPA IBAN (~100%)", "Coverage": "100% (10.0M)"},
            {"Priority": "Tier 3 (Graph)", "Rule Summary": "Romance 1.5×/step escalation; Duplicate 1.0× replay; Mule fan-in (≤13)", "Coverage": "0.07% (7,006)"}
        ])
        st.table(prio_df)
    with c2:
        st.markdown("**2. Data Preparation & Integrity Audit Log (Rubric 3.1)**")
        prep_df = pd.DataFrame([
            {"Field / Issue": "DISCLAIMER", "Audit Finding": "100% Null (10M missing)", "Decision": "Dropped metadata column."},
            {"Field / Issue": "ANOMALY_TYPE", "Audit Finding": "99.93% Null (normal traffic)", "Decision": "Imputed as 'NORMAL' baseline."},
            {"Field / Issue": "*_DETAILS", "Audit Finding": "Embedded line breaks", "Decision": "Used engineered *_TOKENS."},
            {"Field / Issue": "USD_AMOUNT", "Audit Finding": "0 negatives; max $15.6B outlier", "Decision": "Used medians & log scales."},
            {"Field / Issue": "CUSTOMER_RECALL", "Audit Finding": "317 rows (undocumented)", "Decision": "Extracted via full 10M scan."}
        ])
        st.table(prep_df)

    st.markdown("""
    <div class="econ-box">
    <b>Rubric 2.2 & 3.4 Compliance & Tool Disclosure:</b> Executed exclusively on the official Swift synthetic dataset (0 external primary datasets used) using Python 3.13 (<code>pandas</code>, <code>numpy</code>, <code>streamlit</code>, <code>plotly</code>). Per Swift documentation, baseline country/currency frequencies use randomized synthetic distributions rather than confidential network market shares; all rules model conditional structural mechanics.
    </div>
    """, unsafe_allow_html=True)

if view_mode == "All 7 Dashboards (PDF Export View)":
    show_header_kpis()
    show_d1(); show_d2(); show_d3(); show_d4(); show_d5(); show_d6(); show_d7()
elif "Dashboard 1" in view_mode: show_d1()
elif "Dashboard 2" in view_mode: show_d2()
elif "Dashboard 3" in view_mode: show_d3()
elif "Dashboard 4" in view_mode: show_d4()
elif "Dashboard 5" in view_mode: show_d5()
elif "Dashboard 6" in view_mode: show_d6()
elif "Dashboard 7" in view_mode: show_d7()