import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# Halaman & Tema
# =========================
st.set_page_config(page_title="📦 Dashboard Analyst Delivery & Sales", layout="wide")

# =========================
# CSS Custom
# =========================
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #fafafa;
    }
    h1, h2, h3, h4 {
        color: #00FFAA !important;
        text-shadow: 0 0 10px #00FFAA;
    }
    .metric-box {
        padding: 15px;
        border-radius: 12px;
        background: #1e1e1e;
        color: white;
        box-shadow: 0 0 15px rgba(0,255,170,0.4);
        text-align: center;
        margin: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# Upload File
# =========================
st.sidebar.header("📂 Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload file Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Pastikan kolom yang dibutuhkan ada
    required_columns = ["Dp Date", "Salesman Name", "End Customer Name", "Truck No", "DP No", "Qty"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        st.error("❌ File tidak sesuai format. Kolom hilang: " + ", ".join(missing))
    else:
        # =========================
        # Persiapan Data
        # =========================
        df["Dp Date"] = pd.to_datetime(df["Dp Date"])
        df["Ritase"] = 1  # DP No dianggap 1 trip

        # Filter tanggal
        start_date = st.sidebar.date_input("Start Date", df["Dp Date"].min())
        end_date = st.sidebar.date_input("End Date", df["Dp Date"].max())
        df_filtered = df[(df["Dp Date"] >= pd.to_datetime(start_date)) & 
                         (df["Dp Date"] <= pd.to_datetime(end_date))]

        # Filter tambahan
        area_filter = st.sidebar.multiselect("Pilih Area", df_filtered["Area"].unique() if "Area" in df_filtered.columns else [])
        if area_filter:
            df_filtered = df_filtered[df_filtered["Area"].isin(area_filter)]

        plant_filter = st.sidebar.multiselect("Pilih Plant", df_filtered["Plant"].unique() if "Plant" in df_filtered.columns else [])
        if plant_filter:
            df_filtered = df_filtered[df_filtered["Plant"].isin(plant_filter)]

        sales_filter = st.sidebar.multiselect("Pilih Salesman", df_filtered["Salesman Name"].unique())
        if sales_filter:
            df_filtered = df_filtered[df_filtered["Salesman Name"].isin(sales_filter)]

        cust_filter = st.sidebar.multiselect("Pilih Customer", df_filtered["End Customer Name"].unique())
        if cust_filter:
            df_filtered = df_filtered[df_filtered["End Customer Name"].isin(cust_filter)]

        # =========================
        # Header
        # =========================
        st.title("📦 Dashboard Analyst Delivery & Sales")

        # =========================
        # Summary
        # =========================
        st.subheader("📋 Summarize")
        total_trip = df_filtered["Ritase"].sum()
        total_volume = df_filtered["Qty"].sum()
        total_salesman = df_filtered["Salesman Name"].nunique()
        total_customer = df_filtered["End Customer Name"].nunique()
        total_truck = df_filtered["Truck No"].nunique()

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(f"<div class='metric-box'>🚚<br>Total Ritase<br><b>{total_trip}</b></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric-box'>📦<br>Total Volume<br><b>{total_volume}</b></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='metric-box'>👨‍💼<br>Salesman<br><b>{total_salesman}</b></div>", unsafe_allow_html=True)
        with col4:
            st.markdown(f"<div class='metric-box'>🏬<br>Customer<br><b>{total_customer}</b></div>", unsafe_allow_html=True)
        with col5:
            st.markdown(f"<div class='metric-box'>🚛<br>Truck<br><b>{total_truck}</b></div>", unsafe_allow_html=True)

        # =========================
        # 1. Delivery Performance
        # =========================
        st.subheader("🚚 Delivery Performance")
        delivery = df_filtered.groupby("Dp Date").agg(
            Ritase=("Ritase", "sum"),
            Volume=("Qty", "sum")
        ).reset_index()

        fig_delivery = px.bar(delivery, x="Dp Date", y=["Ritase", "Volume"],
                              barmode="group", title="Delivery Performance (Ritase & Volume)")
        st.plotly_chart(fig_delivery, use_container_width=True)

        # =========================
        # 2. Truck Utilization
        # =========================
        st.subheader("🚛 Truck Utilization")
        truck_util = df_filtered.groupby("Truck No").agg(
            Total_Trip=("Ritase", "sum"),
            Total_Volume=("Qty", "sum"),
            Avg_Load_Per_Trip=("Qty", "mean")
        ).reset_index()

        fig_truck = px.bar(truck_util, x="Truck No", y="Total_Volume",
                           hover_data=["Total_Trip", "Avg_Load_Per_Trip"],
                           color="Total_Trip", color_continuous_scale="Viridis",
                           title="Truck Utilization (Volume & Trip)")
        st.plotly_chart(fig_truck, use_container_width=True)

        # =========================
        # 3. Sales Performance
        # =========================
        st.subheader("👨‍💼 Sales Performance")
        sales_perf = df_filtered.groupby("Salesman Name").agg(
            Volume=("Qty", "sum"),
            Trip=("Ritase", "sum")
        ).reset_index()

        fig_sales = px.bar(sales_perf, x="Salesman Name", y="Volume",
                           hover_data=["Trip"], color="Trip",
                           color_continuous_scale="Plasma",
                           title="Volume per Salesman")
        st.plotly_chart(fig_sales, use_container_width=True)

        # =========================
        # 4. Customer Performance
        # =========================
        st.subheader("🏬 Customer Performance")
        cust_perf = df_filtered.groupby("End Customer Name").agg(
            Volume=("Qty", "sum"),
            Trip=("Ritase", "sum")
        ).reset_index()

        fig_cust = px.bar(cust_perf, x="End Customer Name", y="Volume",
                          hover_data=["Trip"], color="Trip",
                          color_continuous_scale="Cividis",
                          title="Volume per End Customer")
        st.plotly_chart(fig_cust, use_container_width=True)

        # =========================
        # 5. Trend (Ritase & Volume)
        # =========================
        st.subheader("📈 Visualisasi Tren")
        trend_ritase = df_filtered.groupby("Dp Date")["Ritase"].sum().reset_index()
        trend_volume = df_filtered.groupby("Dp Date")["Qty"].sum().reset_index()

        fig_trend = px.line(trend_ritase, x="Dp Date", y="Ritase", markers=True, title="Trend Ritase")
        st.plotly_chart(fig_trend, use_container_width=True)

        fig_trend_vol = px.line(trend_volume, x="Dp Date", y="Qty", markers=True, title="Trend Volume")
        st.plotly_chart(fig_trend_vol, use_container_width=True)

        # =========================
        # 6. Distance Analysis
        # =========================
        if "Distance" in df_filtered.columns:
            st.subheader("📍 Distance Analysis")
            distance_analysis = df_filtered.groupby("Truck No")["Distance"].sum().reset_index()

            fig_distance = px.bar(distance_analysis, x="Truck No", y="Distance",
                                  title="Total Distance per Truck", color="Distance",
                                  color_continuous_scale="Blues")
            st.plotly_chart(fig_distance, use_container_width=True)
else:
    st.info("👆 Silakan upload file Excel untuk melihat dashboard.")
