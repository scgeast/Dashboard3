import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# Halaman & Tema
# =========================
st.set_page_config(page_title="📦 Dashboard Analyst Delivery & Sales", layout="wide")

# =========================
# Upload File
# =========================
st.sidebar.header("📂 Upload File Excel")
file = st.sidebar.file_uploader("Upload file Excel", type=["xlsx"])

# =========================
# Fungsi Normalisasi Nama Kolom
# =========================
def normalize_columns(df):
    mapping = {
        "dp date": ["tanggal pengiriman", "delivery date", "dp date"],
        "qty": ["qty", "volume"],
        "sales man": ["sales man", "salesman", "sales name"],
        "dp no": ["dp no", "trip", "ritase"],
        "truck no": ["truck no", "truck"],
        "end customer name": ["end customer name", "customer", "customer name"],
        "area": ["area"],
        "plant": ["plant"],
        "distance": ["distance", "jarak"]
    }

    col_map = {}
    for std_col, variants in mapping.items():
        for v in variants:
            for col in df.columns:
                if col.strip().lower() == v.strip().lower():
                    col_map[col] = std_col
    return df.rename(columns=col_map)

# =========================
# Load Data
# =========================
if file:
    df = pd.read_excel(file)
    df = normalize_columns(df)

    # pastikan kolom wajib ada
    required = ["dp date", "qty", "sales man", "dp no"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        st.error(f"❌ File tidak sesuai format. Kolom hilang: {', '.join(missing)}")
        st.stop()

    # ubah tipe data tanggal
    df["dp date"] = pd.to_datetime(df["dp date"], errors="coerce")

    # =========================
    # Filter Sidebar
    # =========================
    start_date = st.sidebar.date_input("Start Date", df["dp date"].min())
    end_date = st.sidebar.date_input("End Date", df["dp date"].max())
    df_filtered = df[(df["dp date"] >= pd.to_datetime(start_date)) & 
                     (df["dp date"] <= pd.to_datetime(end_date))]

    if "area" in df.columns:
        area_filter = st.sidebar.multiselect("Filter Area", df["area"].unique())
        if area_filter:
            df_filtered = df_filtered[df_filtered["area"].isin(area_filter)]

    if "plant" in df.columns:
        plant_filter = st.sidebar.multiselect("Filter Plant", df["plant"].unique())
        if plant_filter:
            df_filtered = df_filtered[df_filtered["plant"].isin(plant_filter)]

    # =========================
    # Summary Metrics
    # =========================
    total_volume = df_filtered["qty"].sum()
    total_trip = df_filtered["dp no"].count()
    total_truck = df_filtered["truck no"].nunique() if "truck no" in df_filtered.columns else 1
    total_days = df_filtered["dp date"].nunique()

    avg_load_per_day = total_volume / total_days if total_days > 0 else 0
    avg_trip_per_truck = total_trip / total_truck if total_truck > 0 else 0
    volume_per_day = total_volume / total_days if total_days > 0 else 0
    trip_per_day = total_trip / total_days if total_days > 0 else 0

    st.markdown("## 📊 Summarize")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total Volume", f"{total_volume:,.0f}")
    col2.metric("Total Ritase", f"{total_trip:,.0f}")
    col3.metric("Avg Load / Day", f"{avg_load_per_day:,.2f}")
    col4.metric("Avg Trip / Truck", f"{avg_trip_per_truck:,.2f}")
    col5.metric("Volume / Day", f"{volume_per_day:,.2f}")
    col6.metric("Trip / Day", f"{trip_per_day:,.2f}")

    # =========================
    # Delivery Performance
    # =========================
    st.subheader("🚚 Delivery Performance")
    delivery = df_filtered.groupby("dp date").agg(
        Ritase=("dp no", "count"),
        Volume=("qty", "sum")
    ).reset_index()

    fig_delivery = px.bar(delivery, x="dp date", y=["Ritase", "Volume"], barmode="group", title="Delivery Performance")
    st.plotly_chart(fig_delivery, use_container_width=True)

    # =========================
    # Truck Utilization
    # =========================
    st.subheader("🚛 Truck Utilization")
    if "truck no" in df_filtered.columns:
        truck_util = df_filtered.groupby("truck no").agg(
            Total_Volume=("qty", "sum"),
            Total_Trip=("dp no", "count")
        ).reset_index()
        fig_truck = px.bar(truck_util, x="truck no", y="Total_Volume", text="Total_Trip", title="Truck Utilization")
        st.plotly_chart(fig_truck, use_container_width=True)

    # =========================
    # Sales Performance
    # =========================
    st.subheader("👨‍💼 Sales Performance")
    sales_perf = df_filtered.groupby("sales man").agg(
        Volume=("qty", "sum"),
        Trip=("dp no", "count")
    ).reset_index()
    fig_sales = px.bar(sales_perf, x="sales man", y="Volume", text="Trip", title="Sales Performance")
    st.plotly_chart(fig_sales, use_container_width=True)

    # =========================
    # Customer Performance
    # =========================
    if "end customer name" in df_filtered.columns:
        st.subheader("🏢 Customer Performance")
        cust_perf = df_filtered.groupby("end customer name").agg(
            Volume=("qty", "sum"),
            Trip=("dp no", "count")
        ).reset_index()
        fig_cust = px.bar(cust_perf, x="end customer name", y="Volume", text="Trip", title="Customer Performance")
        st.plotly_chart(fig_cust, use_container_width=True)

    # =========================
    # Distance Analysis
    # =========================
    if "distance" in df_filtered.columns:
        st.subheader("📏 Distance Analysis")
        dist_analysis = df_filtered.groupby("dp date")["distance"].mean().reset_index()
        fig_dist = px.line(dist_analysis, x="dp date", y="distance", title="Rata-rata Jarak Pengiriman")
        st.plotly_chart(fig_dist, use_container_width=True)

else:
    st.info("⬆️ Silakan upload file Excel terlebih dahulu.")
