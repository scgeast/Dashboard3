import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# Halaman & Tema
# =========================
st.set_page_config(page_title="📦 Dashboard Analyst Delivery & Sales", layout="wide")
color_palette = ["#00FFFF", "#8A2BE2", "#00FF00", "#FF00FF", "#FFD700"]

# =========================
# Upload File
# =========================
st.sidebar.header("📂 Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload file Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Pastikan kolom yang dibutuhkan ada
    required_columns = ["Tanggal Pengiriman", "Salesman Name", "End Customer Name", "Truck No", "DP No", "Qty"]
    if not all(col in df.columns for col in required_columns):
        st.error("❌ File tidak sesuai format. Pastikan ada kolom: " + ", ".join(required_columns))
    else:
        # =========================
        # Persiapan Data
        # =========================
        df["Tanggal Pengiriman"] = pd.to_datetime(df["Tanggal Pengiriman"])
        df["Ritase"] = 1  # DP No dianggap 1 trip

        # Filter tanggal
        start_date = st.sidebar.date_input("Start Date", df["Tanggal Pengiriman"].min())
        end_date = st.sidebar.date_input("End Date", df["Tanggal Pengiriman"].max())
        df_filtered = df[(df["Tanggal Pengiriman"] >= pd.to_datetime(start_date)) & 
                         (df["Tanggal Pengiriman"] <= pd.to_datetime(end_date))]

        # =========================
        # Header
        # =========================
        st.title("📦 Dashboard Analyst Delivery & Sales")

        # =========================
        # 1. Delivery Performance
        # =========================
        st.subheader("🚚 Delivery Performance")
        delivery = df_filtered.groupby("Tanggal Pengiriman").agg(
            Ritase=("Ritase", "sum"),
            Volume=("Qty", "sum")
        ).reset_index()

        fig_delivery = px.bar(delivery, x="Tanggal Pengiriman", y=["Ritase", "Volume"],
                              barmode="group", color_discrete_sequence=color_palette,
                              title="Delivery Performance (Ritase & Volume)")
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
        # 3. Distance Analysis (dummy contoh)
        # =========================
        st.subheader("📍 Distance Analysis")
        distance_data = df_filtered.groupby("End Customer Name").agg(
            Total_Volume=("Qty", "sum"),
            Total_Trip=("Ritase", "sum")
        ).reset_index()

        fig_distance = px.pie(distance_data, values="Total_Volume", names="End Customer Name",
                              title="Distribusi Volume per End Customer")
        st.plotly_chart(fig_distance, use_container_width=True)

        # =========================
        # 4. Sales & Customer Performance
        # =========================
        st.subheader("📊 Sales & Customer Performance")

        # Volume per Salesman = Sum Qty
        sales_perf = df_filtered.groupby("Salesman Name").agg(
            Volume=("Qty", "sum"),
            Trip=("Ritase", "sum")
        ).reset_index()

        fig_sales = px.bar(sales_perf, x="Salesman Name", y="Volume",
                           hover_data=["Trip"], color="Trip",
                           color_continuous_scale="Plasma",
                           title="Volume per Salesman")
        st.plotly_chart(fig_sales, use_container_width=True)

        # Volume per End Customer = Sum Qty
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
        # 📈 Visualisasi Tren
        # =========================
        st.subheader("📈 Visualisasi Tren")

        trend_ritase = df_filtered.groupby("Tanggal Pengiriman")["Ritase"].sum().reset_index()
        trend_volume = df_filtered.groupby("Tanggal Pengiriman")["Qty"].sum().reset_index()

        fig_trend = px.line(trend_ritase, x="Tanggal Pengiriman", y="Ritase", title="Trend Ritase")
        st.plotly_chart(fig_trend, use_container_width=True)

        fig_trend_vol = px.line(trend_volume, x="Tanggal Pengiriman", y="Qty", title="Trend Volume")
        st.plotly_chart(fig_trend_vol, use_container_width=True)

        # =========================
        # Summary
        # =========================
        st.subheader("📋 Summarize")
        total_trip = df_filtered["Ritase"].sum()
        total_volume = df_filtered["Qty"].sum()
        total_salesman = df_filtered["Salesman Name"].nunique()
        total_customer = df_filtered["End Customer Name"].nunique()
        total_truck = df_filtered["Truck No"].nunique()

        st.markdown(f"""
        - 🚚 **Total Ritase**: {total_trip}  
        - 📦 **Total Volume**: {total_volume}  
        - 👨‍💼 **Jumlah Salesman**: {total_salesman}  
        - 🏬 **Jumlah Customer**: {total_customer}  
        - 🚛 **Jumlah Truck**: {total_truck}  
        """)
else:
    st.info("👆 Silakan upload file Excel untuk melihat dashboard.")
