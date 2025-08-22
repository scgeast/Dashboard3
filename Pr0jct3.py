import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =========================
# Config Halaman
# =========================
st.set_page_config(page_title="🚚 Dashboard Monitoring Delivery And Sales", layout="wide")

# =========================
# Mode Tampilan
# =========================
st.sidebar.header("🎨 Display Mode")
theme = st.sidebar.radio("Pilih Mode", ["Light", "Dark"], horizontal=True)

if theme == "Dark":
    bg_color = "#0e1117"
    font_color = "white"
    chart_template = "plotly_dark"
else:
    bg_color = "white"
    font_color = "black"
    chart_template = "plotly_white"

st.markdown(
    f"""
    <h1 style='text-align: center; color:{font_color};'>
        🚀 Dashboard Monitoring Delivery And Sales
        <span style='float:right; font-size:16px;'>{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</span>
    </h1>
    """,
    unsafe_allow_html=True
)

# =========================
# Upload File Excel
# =========================
uploaded_file = st.file_uploader("📂 Upload File Excel", type=["xlsx", "xls"])

if uploaded_file:
    file_size = uploaded_file.size / (1024 * 1024)  # ukuran MB
    if file_size < 2 or file_size > 50:
        st.error("⚠️ File harus berukuran antara 2MB - 50MB")
    else:
        # Baca file
        df = pd.ExcelFile(uploaded_file).parse(0)

        # Normalisasi kolom
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
            "end customer name": "end_customer",
            "truck no": "truck_no"
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
        # Summarize Box
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
        col1.metric("🌍 Total Area", f"{total_area:,}")
        col2.metric("🏭 Total Plant", f"{total_plant:,}")
        col3.metric("📦 Total Volume", f"{total_volume:,.0f}")
        col4.metric("📅 Avg Volume/Day", f"{avg_volume_day:,.2f}")
        col5.metric("🚚 Total Trip", f"{total_trip:,}")
        col6.metric("⚖️ Avg Load/Trip", f"{avg_load_trip:,.2f}")

        # =========================
        # Pilihan Dashboard
        # =========================
        pilihan = st.radio("📌 Pilih Dashboard", ["Logistic", "Sales & End Customer"], horizontal=True)

        # ----------------------------------------------------
        # Pilihan 1: Logistic
        # ----------------------------------------------------
        if pilihan == "Logistic":
            st.header("📦 Logistic Dashboard")

            # ========== A. Delivery Performance ==========
            st.subheader("🚚 Delivery Performance per Day")

            # Chart 1. Total Volume per Day
            vol_day = df_filtered.groupby("tanggal_pengiriman")["volume"].sum().reset_index()
            fig1 = px.bar(vol_day, x="tanggal_pengiriman", y="volume", template=chart_template,
                          title="Total Volume per Day")
            fig1.update_traces(texttemplate='%{y:,.0f}', textposition="outside")
            st.plotly_chart(fig1, use_container_width=True)

            # Chart 2. Total Volume per Day per Area
            if "area" in df_filtered.columns:
                vol_area = df_filtered.groupby(["tanggal_pengiriman", "area"])["volume"].sum().reset_index()
                fig2 = px.bar(vol_area, x="tanggal_pengiriman", y="volume", color="area",
                              template=chart_template, title="Total Volume per Day per Area")
                st.plotly_chart(fig2, use_container_width=True)

            # Chart 3. Total Volume per Day per Plant Name
            if "plant_name" in df_filtered.columns:
                vol_plant = df_filtered.groupby(["tanggal_pengiriman", "plant_name"])["volume"].sum().reset_index()
                fig3 = px.bar(vol_plant, x="tanggal_pengiriman", y="volume", color="plant_name",
                              template=chart_template, title="Total Volume per Day per Plant Name")
                st.plotly_chart(fig3, use_container_width=True)

            # Chart 4–6 Avg Calculation
            # (dibuat summary bar chart per area/plant dgn rata-rata per hari)
            if total_days > 0:
                if "area" in df_filtered.columns:
                    avg_area = df_filtered.groupby("area")["volume"].sum().reset_index()
                    avg_area["avg"] = avg_area["volume"] / total_days
                    fig5 = px.bar(avg_area.sort_values("avg", ascending=False),
                                  x="area", y="avg", template=chart_template,
                                  title="Avg Volume per Day per Area")
                    fig5.update_traces(texttemplate='%{y:,.2f}', textposition="outside")
                    st.plotly_chart(fig5, use_container_width=True)

                if "plant_name" in df_filtered.columns:
                    avg_plant = df_filtered.groupby("plant_name")["volume"].sum().reset_index()
                    avg_plant["avg"] = avg_plant["volume"] / total_days
                    fig6 = px.bar(avg_plant.sort_values("avg", ascending=False),
                                  x="plant_name", y="avg", template=chart_template,
                                  title="Avg Volume per Day per Plant Name")
                    fig6.update_traces(texttemplate='%{y:,.2f}', textposition="outside")
                    st.plotly_chart(fig6, use_container_width=True)

            # ========== B. Truck Utilization ==========
            st.subheader("🚛 Truck Utilization")

            if "truck_no" in df_filtered.columns:
                truck_vol = df_filtered.groupby("truck_no")["volume"].sum().reset_index()
                fig7 = px.bar(truck_vol.sort_values("volume", ascending=False),
                              x="truck_no", y="volume", template=chart_template,
                              title="Total Volume per Truck")
                st.plotly_chart(fig7, use_container_width=True)

                truck_trip = df_filtered.groupby("truck_no")["trip"].count().reset_index()
                fig8 = px.bar(truck_trip.sort_values("trip", ascending=False),
                              x="truck_no", y="trip", template=chart_template,
                              title="Total Trip per Truck")
                st.plotly_chart(fig8, use_container_width=True)

            # ========== C. Distance Analysis ==========
            st.subheader("📏 Distance Analysis")
            if "area" in df_filtered.columns:
                dist_area = df_filtered.groupby("area")["distance"].mean().reset_index()
                fig9 = px.bar(dist_area.sort_values("distance", ascending=False),
                              x="area", y="distance", template=chart_template,
                              title="Avg Distance per Area")
                st.plotly_chart(fig9, use_container_width=True)

            if "plant_name" in df_filtered.columns:
                dist_plant = df_filtered.groupby("plant_name")["distance"].mean().reset_index()
                fig10 = px.bar(dist_plant.sort_values("distance", ascending=False),
                               x="plant_name", y="distance", template=chart_template,
                               title="Avg Distance per Plant")
                st.plotly_chart(fig10, use_container_width=True)

        # ----------------------------------------------------
        # Pilihan 2: Sales & End Customer
        # ----------------------------------------------------
        elif pilihan == "Sales & End Customer":
            st.header("💼 Sales & End Customer Performance")

            # A. Sales
            st.subheader("🧑‍💼 Sales Performance")
            sales_perf = df_filtered.groupby("salesman")["volume"].sum().reset_index()
            fig11 = px.bar(sales_perf.sort_values("volume", ascending=False),
                           x="salesman", y="volume", template=chart_template,
                           title="Total Volume per Salesman")
            st.plotly_chart(fig11, use_container_width=True)

            # B. End Customer
            if "end_customer" in df_filtered.columns:
                st.subheader("👥 End Customer Performance")
                cust_perf = df_filtered.groupby("end_customer")["volume"].sum().reset_index()
                fig12 = px.bar(cust_perf.sort_values("volume", ascending=False),
                               x="end_customer", y="volume", template=chart_template,
                               title="Total Volume per End Customer")
                st.plotly_chart(fig12, use_container_width=True)
