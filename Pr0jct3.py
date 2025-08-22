import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# =========================
# Page Config
# =========================
st.set_page_config(page_title="🚚 Dashboard Monitoring Delivery And Sales", layout="wide")

# -------------------------
# Theme / Display Mode
# -------------------------
st.sidebar.header("🎨 Display Mode")
theme = st.sidebar.radio("Pilih Mode", ["Light", "Dark"], horizontal=True)

if theme == "Dark":
    chart_template = "plotly_dark"
    base_bg = "#0e1117"
    card_bg = "#111827"
    text_color = "#FFFFFF"
    accent = "#7C3AED"  # futuristic purple
    accent_light = "#A78BFA"
else:
    chart_template = "plotly_white"
    base_bg = "#FFFFFF"
    card_bg = "#F8FAFC"
    text_color = "#111827"
    accent = "#2563EB"  # futuristic blue
    accent_light = "#60A5FA"

st.markdown(
    f"""
    <style>
    .main {{ background-color: {base_bg}; color:{text_color}; }}
    .metric-card {{
        background: linear-gradient(135deg, {card_bg} 0%, {card_bg} 60%, {accent}22 100%);
        border: 1px solid {accent}33; border-radius: 18px; padding: 16px; box-shadow: 0 10px 30px #00000022;
    }}
    .metric-value {{ font-size: 26px; font-weight: 700; color:{text_color}; }}
    .metric-label {{ font-size: 13px; opacity: .8; }}
    .section-title {{ font-size: 22px; font-weight: 700; margin: 8px 0 4px 0; color:{text_color}; }}
    .subtitle {{ font-size: 16px; opacity:.9; margin-bottom:8px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div style='display:flex; align-items:center; justify-content:space-between;'>
      <h1 style='margin:0;color:{text_color}'>🚀 Dashboard Monitoring Delivery And Sales</h1>
      <div style='opacity:.8;color:{text_color}'>Updated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================
# Helpers
# =========================

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.replace("\n", " ")
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", " ", regex=True)
    )
    return df

# Find first matching column name from candidates (case/space-insensitive, supports partials)

def match_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    cols = list(df.columns)
    for cand in candidates:
        # exact
        for c in cols:
            if c == cand:
                return c
        # contains
        for c in cols:
            if cand in c:
                return c
    return None

# Plotly helper with highlight for max bar

def bar_desc(df, x, y, title, color_base, color_highlight, template="plotly_white", show_text=True):
    if df.empty:
        return None
    df = df.copy()
    df[y] = pd.to_numeric(df[y], errors="coerce").fillna(0)
    df = df.sort_values(y, ascending=False)
    max_val = df[y].max()
    colors = [color_highlight if v == max_val else color_base for v in df[y]]
    fig = px.bar(df, x=x, y=y, template=template, title=title)
    fig.update_traces(marker_color=colors)
    if show_text:
        fig.update_traces(texttemplate='%{y:,.2f}', textposition="outside", cliponaxis=False)
    fig.update_layout(xaxis_title=None, yaxis_title=None, bargap=0.35)
    fig.update_yaxes(tickformat=",.0f")
    return fig

# =========================
# Upload Excel
# =========================
uploaded = st.file_uploader("📂 Upload File Excel", type=["xlsx", "xls"])

if uploaded is None:
    st.info("Silakan upload file Excel terlebih dahulu (ukuran 2MB–50MB).")
    st.stop()

size_mb = uploaded.size / (1024 * 1024)
if size_mb < 2 or size_mb > 50:
    st.error("⚠️ File harus berukuran antara 2MB - 50MB")
    st.stop()

# Read first sheet
try:
    df_raw = pd.ExcelFile(uploaded).parse(0)
except Exception as e:
    st.error(f"Gagal membaca file: {e}")
    st.stop()

# Normalize
df = normalize_columns(df_raw)

# Column mapping (flexible)
col_dp_date = match_col(df, ["dp date", "delivery date", "tanggal pengiriman", "delivery date", "dp_date", "tanggal_pengiriman"]) or "dp date"
col_qty     = match_col(df, ["qty", "quantity", "volume"]) or "qty"
col_sales   = match_col(df, ["sales man", "salesman", "sales name", "sales_name"]) or "sales man"
col_dp_no   = match_col(df, ["dp no", "ritase", "dp_no", "trip"]) or "dp no"
col_area    = match_col(df, ["area"]) or None
col_plant   = match_col(df, ["plant name", "plant", "plant_name"]) or None
col_distance= match_col(df, ["distance", "jarak"]) or None
col_truck   = match_col(df, ["truck no", "truck", "truck_no", "nopol", "vehicle"])
col_endcust = match_col(df, ["end customer name", "end customer", "customer", "end_customer"]) or None

# Validate required columns
required = [col_dp_date, col_qty, col_sales, col_dp_no]
req_names_map = {col_dp_date:"Dp Date", col_qty:"Qty", col_sales:"Sales Man", col_dp_no:"Dp No"}
missing = [name for name, label in req_names_map.items() if name is None or name not in df.columns]
if missing:
    st.error("Kolom wajib tidak ditemukan: " + ", ".join([req_names_map[m] if m in req_names_map else m for m in missing]))
    st.stop()

# Coerce types
df[col_dp_date] = pd.to_datetime(df[col_dp_date], errors="coerce")
df = df.dropna(subset=[col_dp_date])
df[col_qty] = pd.to_numeric(df[col_qty], errors="coerce").fillna(0)

# =========================
# Filters (Sidebar)
# =========================
st.sidebar.header("🔍 Filter Data")
min_d = df[col_dp_date].min().date()
max_d = df[col_dp_date].max().date()
start_date = st.sidebar.date_input("Start Date", min_d)
end_date   = st.sidebar.date_input("End Date", max_d)

# Area filter
if col_area:
    areas = ["All"] + sorted([a for a in df[col_area].dropna().astype(str).unique()])
    sel_area = st.sidebar.selectbox("Area", areas)
else:
    sel_area = "All"

# Plant filter (dependent on Area)
if col_plant:
    if col_area and sel_area != "All":
        plants = ["All"] + sorted(df[df[col_area].astype(str) == str(sel_area)][col_plant].dropna().astype(str).unique().tolist())
    else:
        plants = ["All"] + sorted(df[col_plant].dropna().astype(str).unique().tolist())
    sel_plant = st.sidebar.selectbox("Plant Name", plants)
else:
    sel_plant = "All"

# Reset button (simulate by rerun)
if st.sidebar.button("🔄 Reset Filter"):
    st.experimental_rerun()

# Apply filters
mask = (df[col_dp_date].dt.date >= start_date) & (df[col_dp_date].dt.date <= end_date)
if col_area and sel_area != "All":
    mask &= df[col_area].astype(str) == str(sel_area)
if col_plant and sel_plant != "All":
    mask &= df[col_plant].astype(str) == str(sel_plant)

df_f = df.loc[mask].copy()

# Add canonical columns for easier ref
DF_DATE = col_dp_date
DF_QTY = col_qty
DF_SALES = col_sales
DF_TRIP = col_dp_no
DF_AREA = col_area
DF_PLANT = col_plant
DF_DIST = col_distance
DF_TRUCK = col_truck
DF_ENDC = col_endcust

# =========================
# Summarize (KPI Cards)
# =========================
st.markdown("<div class='section-title'>📊 Summarize</div>", unsafe_allow_html=True)

kpi_cols = st.columns(6)

def fmt0(x):
    try:
        return f"{int(x):,}"
    except:
        return "0"

def fmt2(x):
    try:
        return f"{x:,.2f}"
    except:
        return "0.00"

# Total Area & Plant
tot_area = df_f[DF_AREA].nunique() if DF_AREA else 0
tot_plant = df_f[DF_PLANT].nunique() if DF_PLANT else 0

# Total Volume
tot_vol = float(df_f[DF_QTY].sum())

# Total Truck (unique truck_no if exists)
if DF_TRUCK and DF_TRUCK in df_f.columns:
    tot_truck = df_f[DF_TRUCK].nunique()
else:
    tot_truck = 0

# Total Trip per Truck: interpret as total trips across all trucks (unique DP No)
# If file has line-level entries per DP No, use nunique to avoid double-counting
if DF_TRIP in df_f.columns:
    total_trip = df_f[DF_TRIP].nunique()
else:
    total_trip = 0

# Avg Load Truck per Trip = Total Volume / Total Trip (if trip>0)
avg_load_trip = (tot_vol / total_trip) if total_trip > 0 else 0

# Render KPI cards
kpis = [
    ("🌍 Total Area", fmt0(tot_area)),
    ("🏭 Total Plant", fmt0(tot_plant)),
    ("📦 Total Volume", fmt0(round(tot_vol))),
    ("🚛 Total Truck", fmt0(tot_truck)),
    ("🧾 Total Trip per Truck", fmt0(total_trip)),
    ("⚖️ Avg Load per Trip", fmt2(avg_load_trip)),
]

for col, (label, value) in zip(kpi_cols, kpis):
    with col:
        st.markdown("<div class='metric-card'>" \
                    f"<div class='metric-label'>{label}</div>" \
                    f"<div class='metric-value'>{value}</div>" \
                    "</div>", unsafe_allow_html=True)

st.markdown("""
<hr style='opacity:.2;'>
""", unsafe_allow_html=True)

# =========================
# Dashboard Switcher
# =========================
pick = st.radio("📌 Pilih Dashboard", ["Logistic", "Sales & End Customer"], horizontal=True)

# Utility for day span
day_span = max((end_date - start_date).days + 1, 1)

# ----------------------------------------------------
# DASHBOARD 1: LOGISTIC
# ----------------------------------------------------
if pick == "Logistic":
    st.markdown("<div class='section-title'>📦 Logistic</div>", unsafe_allow_html=True)

    # ---------- A. Delivery Performance per Day ----------
    st.markdown("<div class='subtitle'>🚚 Delivery Performance per Day</div>", unsafe_allow_html=True)

    # Chart 1: Total Volume per Day
    vol_day = df_f.groupby(DF_DATE, as_index=False)[DF_QTY].sum().rename(columns={DF_QTY: "Total Volume"})
    fig1 = bar_desc(vol_day, DF_DATE, "Total Volume", "Total Volume per Day", accent, accent_light, chart_template)
    if fig1:
        st.plotly_chart(fig1, use_container_width=True)

    # Chart 2: Total Volume per Area (Pie)
    if DF_AREA:
        vol_area = df_f.groupby(DF_AREA, as_index=False)[DF_QTY].sum().rename(columns={DF_QTY: "Volume"})
        vol_area = vol_area.sort_values("Volume", ascending=False)
        fig2 = px.pie(vol_area, names=DF_AREA, values="Volume", template=chart_template, title="Total Volume per Area (Pie)")
        fig2.update_traces(textposition='inside', texttemplate='%{label}<br>%{value:,.0f} (%{percent})', pull=[0.08 if i==0 else 0 for i in range(len(vol_area))])
        st.plotly_chart(fig2, use_container_width=True)

    # Chart 3: Total Volume per Plant Name
    if DF_PLANT:
        vol_plant = df_f.groupby(DF_PLANT, as_index=False)[DF_QTY].sum().rename(columns={DF_QTY: "Total Volume"})
        fig3 = bar_desc(vol_plant, DF_PLANT, "Total Volume", "Total Volume per Plant Name", accent, accent_light, chart_template)
        if fig3:
            st.plotly_chart(fig3, use_container_width=True)

    # Chart 4: Avg Volume per Day (overall)
    avg_day_overall = pd.DataFrame({"Metric": ["Avg Volume / Day"], "Value": [tot_vol / day_span if day_span>0 else 0]})
    fig4 = bar_desc(avg_day_overall, "Metric", "Value", "Avg Volume per Day (Overall)", accent, accent_light, chart_template)
    if fig4:
        fig4.update_traces(texttemplate='%{y:,.2f}')
        st.plotly_chart(fig4, use_container_width=True)

    # Chart 5: Avg Volume per Day per Area
    if DF_AREA:
        avg_area = df_f.groupby(DF_AREA, as_index=False)[DF_QTY].sum()
        avg_area["Avg/Day"] = avg_area[DF_QTY] / day_span
        fig5 = bar_desc(avg_area[[DF_AREA, "Avg/Day"]], DF_AREA, "Avg/Day", "Avg Volume per Day per Area", accent, accent_light, chart_template)
        if fig5:
            st.plotly_chart(fig5, use_container_width=True)

    # Chart 6: Avg Volume per Day per Plant Name
    if DF_PLANT:
        avg_plant = df_f.groupby(DF_PLANT, as_index=False)[DF_QTY].sum()
        avg_plant["Avg/Day"] = avg_plant[DF_QTY] / day_span
        fig6 = bar_desc(avg_plant[[DF_PLANT, "Avg/Day"]], DF_PLANT, "Avg/Day", "Avg Volume per Day per Plant Name", accent, accent_light, chart_template)
        if fig6:
            st.plotly_chart(fig6, use_container_width=True)

    # ---------- B. Truck Utilization ----------
    st.markdown("<div class='subtitle'>🚛 Truck Utilization</div>", unsafe_allow_html=True)

    if DF_TRUCK:
        # Chart 1: Total Volume per Truck (Sum Qty per Truck No)
        truck_vol = df_f.groupby(DF_TRUCK, as_index=False)[DF_QTY].sum().rename(columns={DF_QTY: "Total Volume"})
        fig7 = bar_desc(truck_vol, DF_TRUCK, "Total Volume", "Total Volume per Truck", accent, accent_light, chart_template)
        if fig7:
            st.plotly_chart(fig7, use_container_width=True)

        # Chart 2: Total Trip per Truck (unique DP No per truck)
        trips_per_truck = df_f.groupby(DF_TRUCK, as_index=False)[DF_TRIP].nunique().rename(columns={DF_TRIP: "Total Trip"})
        fig8 = bar_desc(trips_per_truck, DF_TRUCK, "Total Trip", "Total Trip per Truck", accent, accent_light, chart_template)
        if fig8:
            fig8.update_traces(texttemplate='%{y:,.0f}')
            st.plotly_chart(fig8, use_container_width=True)

        # Chart 3: Avg Load per Trip per Truck = Total Volume per Truck / Total Trip per Truck
        avg_load = pd.merge(truck_vol, trips_per_truck, on=DF_TRUCK, how='left')
        avg_load["Avg Load/Trip"] = np.where(avg_load["Total Trip"]>0, avg_load["Total Volume"] / avg_load["Total Trip"], 0)
        fig9 = bar_desc(avg_load[[DF_TRUCK, "Avg Load/Trip"]], DF_TRUCK, "Avg Load/Trip", "Avg Load per Trip per Truck", accent, accent_light, chart_template)
        if fig9:
            st.plotly_chart(fig9, use_container_width=True)

        # Chart 4: Avg Trip per Truck per Day = (Total Trip per Truck / Total Hari Filter)
        avg_trip_day = trips_per_truck.copy()
        avg_trip_day["Avg Trip/Day"] = avg_trip_day["Total Trip"] / day_span if day_span>0 else 0
        fig10 = bar_desc(avg_trip_day[[DF_TRUCK, "Avg Trip/Day"]], DF_TRUCK, "Avg Trip/Day", "Avg Trip per Truck per Day", accent, accent_light, chart_template)
        if fig10:
            fig10.update_traces(texttemplate='%{y:,.2f}')
            st.plotly_chart(fig10, use_container_width=True)
    else:
        st.info("Kolom Truck No tidak ditemukan. Bagian Truck Utilization memerlukan kolom `Truck No`." )

    # ---------- C. Distance Analysis ----------
    st.markdown("<div class='subtitle'>📏 Distance Analysis</div>", unsafe_allow_html=True)
    if DF_DIST is None:
        st.info("Kolom Distance tidak ditemukan di file. Bagian Distance Analysis dilewati.")
    else:
        if DF_AREA:
            dist_area = df_f.groupby(DF_AREA, as_index=False)[DF_DIST].mean().rename(columns={DF_DIST: "Avg Distance"})
            fig11 = bar_desc(dist_area, DF_AREA, "Avg Distance", "Avg Distance per Area", accent, accent_light, chart_template)
            if fig11:
                fig11.update_traces(texttemplate='%{y:,.2f}')
                st.plotly_chart(fig11, use_container_width=True)
        if DF_PLANT:
            dist_plant = df_f.groupby(DF_PLANT, as_index=False)[DF_DIST].mean().rename(columns={DF_DIST: "Avg Distance"})
            fig12 = bar_desc(dist_plant, DF_PLANT, "Avg Distance", "Avg Distance per Plant", accent, accent_light, chart_template)
            if fig12:
                fig12.update_traces(texttemplate='%{y:,.2f}')
                st.plotly_chart(fig12, use_container_width=True)

# ----------------------------------------------------
# DASHBOARD 2: SALES & END CUSTOMER
# ----------------------------------------------------
if pick == "Sales & End Customer":
    st.markdown("<div class='section-title'>💼 Sales & End Customer Performance</div>", unsafe_allow_html=True)

    # A. Sales
    st.markdown("<div class='subtitle'>🧑‍💼 Sales</div>", unsafe_allow_html=True)
    sales = df_f.groupby(DF_SALES, as_index=False)[DF_QTY].sum().rename(columns={DF_QTY: "Total Volume"})
    figA = bar_desc(sales, DF_SALES, "Total Volume", "Total Volume per Sales Man", accent, accent_light, chart_template)
    if figA:
        st.plotly_chart(figA, use_container_width=True)

    # B. End Customer
    if DF_ENDC:
        st.markdown("<div class='subtitle'>👥 End Customer</div>", unsafe_allow_html=True)
        endc = df_f.groupby(DF_ENDC, as_index=False)[DF_QTY].sum().rename(columns={DF_QTY: "Total Volume"})
        figB = bar_desc(endc, DF_ENDC, "Total Volume", "Total Volume per End Customer Name", accent, accent_light, chart_template)
        if figB:
            st.plotly_chart(figB, use_container_width=True)
    else:
        st.info("Kolom End Customer Name tidak ditemukan di file.")

# Notes:
# - Semua bar chart di-sort descending (kiri->kanan) melalui bar_desc()
# - Label angka tampil di atas bar dengan format ribuan dan 2 desimal untuk Avg.
# - Pie chart Area menonjolkan slice terbesar (pull pada indeks 0 setelah sort descending).
# - Mode gelap/terang mempengaruhi warna teks & template chart.
