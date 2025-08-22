import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# Halaman & Tema
# =========================
st.set_page_config(page_title="📦 Dashboard Analyst Delivery & Sales", layout="wide")
color_palette = ["#00FFFF","#8A2BE2","#00FF00","#FF00FF","#FFD700"]

st.title("📦 Dashboard Analyst Delivery & Sales")

# =========================
# Upload File
# =========================
uploaded_file = st.file_uploader("📂 Upload file Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # =========================
    # Normalisasi Kolom
    # =========================
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "")

    column_map = {
        "dpdate": "dp date",
        "tanggalpengiriman": "dp date",
        "deliverydate": "dp date",
        "qty": "qty",
        "volume": "qty",
        "salesman": "sales man",
        "salesname": "sales man",
        "salesmanname": "sales man",
        "dpno": "dp no",
        "trip": "dp no",
        "ritase": "dp no",
        "truckno": "truck no",
        "endcustomername": "end customer name"
    }

    df = df.rename(columns=lambda x: column_map[x] if x in column_map else x)

    # Pastikan kolom penting ada
    required_cols = ["dp date", "qty", "dp no"]
    for col in required_cols:
        if col not in df.columns:
            st.error(f"❌ File tidak sesuai format. Kolom '{col}' tidak ditemukan.")
            st.stop()

    # =========================
    # Konversi Tanggal
    # =========================
    df["dp date"] = pd.to_datetime(df["dp date"], errors="coerce")

    # =========================
    # Filter Date
    # =========================
    start_date = st.sidebar.date_input("Start Date", df["dp date"].min())
    end_date = st.sidebar.date_input("End Date", df["dp date"].max())
    df_filtered = df[(df["dp date"] >= pd.to_datetime(start_date)) & (df["dp date"] <= pd.to_datetime(end_date))]

    # =========================
    # Summary
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
    # Sales Performance
    # =========================
    if "sales man" in df_filtered.columns:
        st.subheader("👨‍💼 Sales Performance")
        sales_perf = df_filtered.groupby("sales man").agg(
            Volume=("qty", "sum"),
            Trip=("dp no", "count")
        ).reset_index()
        fig_sales = px.bar(sales_perf, x="sales man", y="Volume", text="Trip", title="Sales Performance")
        st.plotly_chart(fig_sales, use_container_width=True)
    else:
        st.warning("⚠️ Kolom *Sales Man* tidak ditemukan.")

    # =========================
    # Customer Performance
    # =========================
    if "end customer name" in df_filtered.columns and df_filtered["end customer name"].ndim == 1:
        st.subheader("🏢 Customer Performance")
        cust_perf = df_filtered.groupby("end customer name").agg(
            Volume=("qty", "sum"),
            Trip=("dp no", "count")
        ).reset_index()
        fig_cust = px.bar(cust_perf, x="end customer name", y="Volume", text="Trip", title="Customer Performance")
        st.plotly_chart(fig_cust, use_container_width=True)
    else:
        st.warning("⚠️ Kolom *End Customer Name* tidak ditemukan.")

    # =========================
    # Truck Utilization
    # =========================
    if "truck no" in df_filtered.columns:
        st.subheader("🚚 Truck Utilization")
        truck_perf = df_filtered.groupby("truck no").agg(
            Volume=("qty", "sum"),
            Trip=("dp no", "count")
        ).reset_index()
        fig_truck = px.bar(truck_perf, x="truck no", y="Volume", text="Trip", title="Truck Utilization")
        st.plotly_chart(fig_truck, use_container_width=True)
    else:
        st.warning("⚠️ Kolom *Truck No* tidak ditemukan.")

    # =========================
    # Delivery Performance per Day
    # =========================
    st.subheader("📦 Delivery Performance per Day")
    daily_perf = df_filtered.groupby("dp date").agg(
        Volume=("qty", "sum"),
        Trip=("dp no", "count")
    ).reset_index()
    fig_delivery = px.line(daily_perf, x="dp date", y="Volume", markers=True, title="Delivery Performance (Volume per Day)")
    fig_delivery.add_bar(x=daily_perf["dp date"], y=daily_perf["Trip"], name="Trip")
    st.plotly_chart(fig_delivery, use_container_width=True)

else:
    st.info("⬆️ Silakan upload file Excel untuk memulai.")
