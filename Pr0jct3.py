# Dashboard2 Final Revisi
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="📦 Dashboard Analyst Delivery & Sales", layout="wide")
st.title("📦 Dashboard Analyst Delivery dan Sales")

# Upload file
uploaded_file = st.file_uploader("Upload file Excel (5MB–30MB)", type=["xlsx", "xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    expected_columns = [
        "Tanggal Pengiriman", "Area", "Plant Name", "Salesman", "End Customer",
        "Volume", "Ritase", "Truck No", "Distance"
    ]
    missing_columns = [col for col in expected_columns if col not in df.columns]

    if missing_columns:
        st.warning(f"Kolom berikut tidak ditemukan di file Excel: {missing_columns}")
    else:
        df["Tanggal Pengiriman"] = pd.to_datetime(df["Tanggal Pengiriman"])

        # Sidebar Filter
        st.sidebar.header("🔎 Filter Data")
        start_date = st.sidebar.date_input("Start Date", df["Tanggal Pengiriman"].min())
        end_date = st.sidebar.date_input("End Date", df["Tanggal Pengiriman"].max())

        area = st.sidebar.multiselect("Area", options=df["Area"].dropna().unique())
        plant_options = df[df["Area"].isin(area)]["Plant Name"].dropna().unique() if area else df["Plant Name"].dropna().unique()
        plant = st.sidebar.multiselect("Plant Name", options=plant_options)
        salesman = st.sidebar.multiselect("Salesman", options=df["Salesman"].dropna().unique())
        end_customer = st.sidebar.multiselect("End Customer", options=df["End Customer"].dropna().unique())

        # Filter Data
        df_filtered = df.copy()
        df_filtered = df_filtered[
            (df_filtered["Tanggal Pengiriman"] >= pd.to_datetime(start_date)) &
            (df_filtered["Tanggal Pengiriman"] <= pd.to_datetime(end_date))
        ]
        if area:
            df_filtered = df_filtered[df_filtered["Area"].isin(area)]
        if plant:
            df_filtered = df_filtered[df_filtered["Plant Name"].isin(plant)]
        if salesman:
            df_filtered = df_filtered[df_filtered["Salesman"].isin(salesman)]
        if end_customer:
            df_filtered = df_filtered[df_filtered["End Customer"].isin(end_customer)]

        # Ekspor Excel
        def to_excel(dataframe):
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                dataframe.to_excel(writer, index=False, sheet_name="Report")
            output.seek(0)
            return output.getvalue()

        excel_data = to_excel(df_filtered)
        st.download_button("📥 Download data sebagai Excel", excel_data, "report.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # 📊 Analisa Volume Penjualan
        st.subheader("📊 Analisa Volume Penjualan")
        sales_trend = df_filtered.groupby("Tanggal Pengiriman")["Volume"].sum().reset_index()
        fig_sales_trend = px.line(sales_trend, x="Tanggal Pengiriman", y="Volume", markers=True,
                                  title="Tren Volume Penjualan")
        fig_sales_trend.update_layout(legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig_sales_trend, use_container_width=True)

        # 📍 Volume per Area & Plant
        col1, col2 = st.columns(2)
        with col1:
            fig_area = px.bar(df_filtered.groupby("Area")["Volume"].sum().reset_index(),
                              x="Area", y="Volume", title="Volume per Area", text="Volume")
            fig_area.update_traces(texttemplate="%{text:.2s}", textposition="outside")
            st.plotly_chart(fig_area, use_container_width=True)

        with col2:
            fig_plant = px.bar(df_filtered.groupby("Plant Name")["Volume"].sum().reset_index(),
                               x="Plant Name", y="Volume", title="Volume per Plant", text="Volume")
            fig_plant.update_traces(texttemplate="%{text:.2s}", textposition="outside")
            st.plotly_chart(fig_plant, use_container_width=True)

        # 👤 Performa Sales & Customer
        st.subheader("👤 Performa Sales & Customer")
        fig_salesman = px.bar(df_filtered.groupby("Salesman")["Volume"].sum().reset_index(),
                              x="Salesman", y="Volume", title="Performa Salesman", text="Volume")
        fig_customer = px.bar(df_filtered.groupby("End Customer")["Volume"].sum().reset_index(),
                              x="End Customer", y="Volume", title="Performa End Customer", text="Volume")
        st.plotly_chart(fig_salesman, use_container_width=True)
        st.plotly_chart(fig_customer, use_container_width=True)

        # 🚚 Optimasi Logistik
        st.subheader("🚚 Optimasi Logistik")
        col3, col4 = st.columns(2)
        with col3:
            fig_truck_total = px.bar(df_filtered.groupby("Truck No")["Ritase"].sum().reset_index(),
                                     x="Truck No", y="Ritase", title="Total Ritase per Truck", text="Ritase")
            st.plotly_chart(fig_truck_total, use_container_width=True)
        with col4:
            fig_truck_avg = px.bar(df_filtered.groupby("Truck No")["Volume"].mean().reset_index(),
                                   x="Truck No", y="Volume", title="Average Volume per Ritase (Truck)", text="Volume")
            st.plotly_chart(fig_truck_avg, use_container_width=True)

        # 📈 Visualisasi Tren
        st.subheader("📈 Visualisasi Tren")
        trend_ritase = df_filtered.groupby("Tanggal Pengiriman")["Ritase"].sum().reset_index()
        trend_volume = df_filtered.groupby("Tanggal Pengiriman")["Volume"].sum().reset_index()
        st.plotly_chart(px.line(trend_ritase, x="Tanggal Pengiriman", y="Ritase", markers=True, title="Tren Ritase"), use_container_width=True)
        st.plotly_chart(px.line(trend_volume, x="Tanggal Pengiriman", y="Volume", markers=True, title="Tren Volume"), use_container_width=True)

        # 📍 Analisa Jarak Tempuh
        st.subheader("📍 Analisa Jarak Tempuh")
        col5, col6 = st.columns(2)
        with col5:
            avg_dist_plant = df_filtered.groupby("Plant Name")["Distance"].mean().reset_index()
            fig_avg_dist_plant = px.bar(avg_dist_plant, x="Plant Name", y="Distance",
                                        title="Average Distance per Plant", text="Distance")
            st.plotly_chart(fig_avg_dist_plant, use_container_width=True)
        with col6:
            avg_dist_area = df_filtered.groupby("Area")["Distance"].mean().reset_index()
            fig_avg_dist_area = px.bar(avg_dist_area, x="Area", y="Distance",
                                       title="Average Distance per Area", text="Distance")
            st.plotly_chart(fig_avg_dist_area, use_container_width=True)
