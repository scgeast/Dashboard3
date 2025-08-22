import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =========================
# Config Halaman
# =========================
st.set_page_config(
    page_title="🚚 Dashboard Monitoring Delivery And Sales",
    layout="wide"
)

st.title("🚀 Dashboard Monitoring Delivery And Sales")

# =========================
# Upload File Excel
# =========================
uploaded_file = st.file_uploader("📂 Upload File Excel", type=["xlsx", "xls"])

if uploaded_file:
    file_size = uploaded_file.size / (1024 * 1024)  # ukuran MB
    if file_size < 5 or file_size > 30:
        st.error("⚠️ File harus berukuran antara 5MB - 30MB")
    else:
        # Baca file
        df = pd.ExcelFile(uploaded_file).parse(0)

        # Normalisasi kolom (hilangkan spasi, lowercase)
        df.columns = df.columns.str.strip().str.lower()

        # Mapping Nama Kolom
        mapping = {
            "dp date": "tanggal_pengiriman",
            "delivery date": "tanggal_pengiriman",
            "qty": "volume",
            "sales man": "salesman",
            "sales name": "salesman",
            "salesman": "salesman",
            "dp no": "trip",
            "ritase": "trip",
            "distance": "distance",
            "area": "area",
            "plant name": "plant_name",
            "end customer name": "end_customer"
        }

        df = df.rename(columns={col: mapping[col] for col in df.columns if col in mapping})

        # Pastikan kolom penting ada
        required_cols = ["tanggal_pengiriman", "volume", "salesman", "trip", "distance"]
        for col in required_cols:
            if col not in df.columns:
                st.error(f"⚠️ Kolom wajib `{col}` tidak ditemukan di file")
                st.stop()

        # Convert Date
        df["tanggal_pengiriman"] = pd.to_datetime(df["tanggal_pengiriman"], errors="coerce")

        # =========================
        # Filter
        # =========================
        st.sidebar.header("🔍 Filter Data")
        start_date = st.sidebar.date_input("Start Date", df["tanggal_pengiriman"].min().date())
        end_date = st.sidebar.date_input("End Date", df["tanggal_pengiriman"].max().date())

        # Filter Area
        area_list = ["All"] + sorted(df["area"].dropna().unique().tolist()) if "area" in df.columns else []
        selected_area = st.sidebar.selectbox("Pilih Area", area_list)

        # Filter Plant
        if selected_area != "All" and "plant_name" in df.columns:
            plant_list = ["All"] + sorted(df[df["area"] == selected_area]["plant_name"].dropna().unique().tolist())
        else:
            plant_list = ["All"] + sorted(df["plant_name"].dropna().unique().tolist()) if "plant_name" in df.columns else []
        selected_plant = st.sidebar.selectbox("Pilih Plant", plant_list)

        # Tombol Reset
        if st.sidebar.button("🔄 Reset Filter"):
            start_date = df["tanggal_pengiriman"].min().date()
            end_date = df["tanggal_pengiriman"].max().date()
            selected_area = "All"
            selected_plant = "All"

        # Apply Filter
        df_filtered = df[
            (df["tanggal_pengiriman"].dt.date >= start_date) &
            (df["tanggal_pengiriman"].dt.date <= end_date)
        ]
        if selected_area != "All":
            df_filtered = df_filtered[df_filtered["area"] == selected_area]
        if selected_plant != "All":
            df_filtered = df_filtered[df_filtered["plant_name"] == selected_plant]

        # =========================
        # Summarize (Kotak Atas)
        # =========================
        st.subheader("📊 Summarize")

        total_area = df_filtered["area"].nunique() if "area" in df_filtered.columns else 0
        total_plant = df_filtered["plant_name"].nunique() if "plant_name" in df_filtered.columns else 0
        total_volume = df_filtered["volume"].sum()
        total_trip = df_filtered["trip"].nunique()
        total_days = (end_date - start_date).days + 1
        avg_volume_day = total_volume / total_days if total_days > 0 else 0
        avg_load_trip = total_volume / total_trip if total_trip > 0 else 0

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("🌍 Total Area", total_area)
        col2.metric("🏭 Total Plant", total_plant)
        col3.metric("📦 Total Volume", int(total_volume))
        col4.metric("📅 Avg Volume/Day", round(avg_volume_day, 2))
        col5.metric("🚚 Total Trip", total_trip)
        col6.metric("⚖️ Avg Load/Trip", round(avg_load_trip, 2))

        # =========================
        # Pilihan Dashboard
        # =========================
        pilihan = st.radio("📌 Pilih Dashboard", ["Logistic", "Sales & End Customer", "KPI"], horizontal=True)

        # ----------------------------------------------------
        # Pilihan 1: Logistic
        # ----------------------------------------------------
        if pilihan == "Logistic":
            st.header("📦 Logistic Dashboard")

            # A. Delivery Performance
            st.subheader("🚚 Delivery Performance per Day")
            vol_day = df_filtered.groupby("tanggal_pengiriman")["volume"].sum().reset_index()
            fig1 = px.line(vol_day, x="tanggal_pengiriman", y="volume", title="Total Volume per Day")
            st.plotly_chart(fig1, use_container_width=True)

            # B. Truck Utilization
            st.subheader("🚛 Truck Utilization")
            truck_util = df_filtered.groupby("trip")["volume"].sum().reset_index()
            fig2 = px.bar(truck_util, x="trip", y="volume", title="Total Volume per Truck")
            st.plotly_chart(fig2, use_container_width=True)

            # C. Distance Analysis
            st.subheader("📏 Distance Analysis")
            if "area" in df_filtered.columns:
                dist_area = df_filtered.groupby("area")["distance"].mean().reset_index()
                fig3 = px.bar(dist_area, x="area", y="distance", title="Avg Distance per Area")
                st.plotly_chart(fig3, use_container_width=True)

        # ----------------------------------------------------
        # Pilihan 2: Sales & End Customer
        # ----------------------------------------------------
        elif pilihan == "Sales & End Customer":
            st.header("💼 Sales & End Customer Performance")

            # A. Sales
            st.subheader("🧑‍💼 Sales Performance")
            sales_perf = df_filtered.groupby("salesman")["volume"].sum().reset_index()
            fig4 = px.bar(sales_perf, x="salesman", y="volume", title="Total Volume per Salesman")
            st.plotly_chart(fig4, use_container_width=True)

            # B. End Customer
            if "end_customer" in df_filtered.columns:
                st.subheader("👥 End Customer Performance")
                cust_perf = df_filtered.groupby("end_customer")["volume"].sum().reset_index()
                fig5 = px.bar(cust_perf, x="end_customer", y="volume", title="Total Volume per End Customer")
                st.plotly_chart(fig5, use_container_width=True)

        # ----------------------------------------------------
        # Pilihan 3: KPI
        # ----------------------------------------------------
        elif pilihan == "KPI":
            st.header("📈 KPI Dashboard")

            kpi1 = round(total_volume / total_days, 2) if total_days > 0 else 0
            kpi2 = round(total_trip / total_days, 2) if total_days > 0 else 0

            col1, col2 = st.columns(2)
            col1.metric("📦 Avg Volume per Day", kpi1)
            col2.metric("🚚 Avg Trip per Day", kpi2)
