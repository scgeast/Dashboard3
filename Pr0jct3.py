import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =========================
# Halaman & Tema
# =========================
st.set_page_config(page_title="📊 Dashboard Monitoring Delivery And Sales", layout="wide")

# Pilihan Mode
mode = st.sidebar.radio("🌗 Pilih Mode Tampilan", ["Light", "Dark"])

if mode == "Dark":
    base_color = "#1E1E1E"
    font_color = "#FFFFFF"
else:
    base_color = "#FFFFFF"
    font_color = "#000000"

# =========================
# Upload File
# =========================
st.title("📦 Dashboard Monitoring Delivery And Sales")
st.markdown(f"<h6 style='text-align:right; color:{font_color};'>⏱️ {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</h6>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 Upload file Excel (2MB - 50MB)", type=["xlsx", "xls"])

if uploaded_file:
    if uploaded_file.size < 2 * 1024 * 1024 or uploaded_file.size > 50 * 1024 * 1024:
        st.error("⚠️ Ukuran file harus antara 2MB sampai 50MB")
    else:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip().str.lower()

        # Mapping kolom
        rename_map = {
            'dp date': 'tanggal pengiriman',
            'delivery date': 'tanggal pengiriman',
            'qty': 'volume',
            'sales man': 'salesman',
            'sales name': 'salesman',
            'dp no': 'ritase',
            'trip': 'ritase'
        }
        df.rename(columns={col: rename_map.get(col, col) for col in df.columns}, inplace=True)

        # Pastikan tipe data
        if 'tanggal pengiriman' in df:
            df['tanggal pengiriman'] = pd.to_datetime(df['tanggal pengiriman'], errors='coerce')

        # =========================
        # Filter
        # =========================
        with st.sidebar:
            st.subheader("🔎 Filter Data")
            start_date = st.date_input("Start Date", value=df['tanggal pengiriman'].min())
            end_date = st.date_input("End Date", value=df['tanggal pengiriman'].max())

            area_options = df['area'].dropna().unique() if 'area' in df else []
            area = st.selectbox("Pilih Area", ["All"] + list(area_options)) if len(area_options) > 0 else "All"

            if area != "All" and 'plant name' in df:
                plant_options = df[df['area'] == area]['plant name'].dropna().unique()
                plant = st.selectbox("Pilih Plant", ["All"] + list(plant_options))
            else:
                plant = "All"

            if st.button("Reset Filter"):
                start_date = df['tanggal pengiriman'].min()
                end_date = df['tanggal pengiriman'].max()
                area = "All"
                plant = "All"

        df_filtered = df.copy()
        if 'tanggal pengiriman' in df_filtered:
            df_filtered = df_filtered[(df_filtered['tanggal pengiriman'] >= pd.to_datetime(start_date)) & (df_filtered['tanggal pengiriman'] <= pd.to_datetime(end_date))]

        if area != "All" and 'area' in df_filtered:
            df_filtered = df_filtered[df_filtered['area'] == area]

        if plant != "All" and 'plant name' in df_filtered:
            df_filtered = df_filtered[df_filtered['plant name'] == plant]

        # =========================
        # Summarize
        # =========================
        st.subheader("📊 Summarize")
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        total_area = df_filtered['area'].nunique() if 'area' in df_filtered else 0
        total_plant = df_filtered['plant name'].nunique() if 'plant name' in df_filtered else 0
        total_volume = df_filtered['volume'].sum() if 'volume' in df_filtered else 0
        total_truck = df_filtered['truck no'].nunique() if 'truck no' in df_filtered else 0
        total_trip = df_filtered['ritase'].nunique() if 'ritase' in df_filtered else 0
        avg_load = total_volume / total_trip if total_trip > 0 else 0

        col1.metric("Total Area", f"{total_area:,}")
        col2.metric("Total Plant", f"{total_plant:,}")
        col3.metric("Total Volume", f"{total_volume:,.0f}")
        col4.metric("Total Truck", f"{total_truck:,}")
        col5.metric("Total Trip", f"{total_trip:,}")
        col6.metric("Avg Load / Trip", f"{avg_load:,.2f}")

        # =========================
        # Tabs Pilihan Dashboard
        # =========================
        tab1, tab2 = st.tabs(["🚛 Logistic", "🛒 Sales & End Customer"])

        with tab1:
            st.subheader("🚛 Delivery Performance per Day")
            if 'volume' in df_filtered:
                chart1 = df_filtered.groupby('tanggal pengiriman')['volume'].sum().reset_index()
                fig1 = px.bar(chart1, x='tanggal pengiriman', y='volume', title="Total Volume per Day")
                st.plotly_chart(fig1, use_container_width=True)

                if 'area' in df_filtered:
                    chart2 = df_filtered.groupby('area')['volume'].sum().reset_index()
                    fig2 = px.pie(chart2, names='area', values='volume', title="Total Volume per Area")
                    st.plotly_chart(fig2, use_container_width=True)

                if 'plant name' in df_filtered:
                    chart3 = df_filtered.groupby('plant name')['volume'].sum().reset_index()
                    fig3 = px.bar(chart3, x='plant name', y='volume', title="Total Volume per Plant Name")
                    st.plotly_chart(fig3, use_container_width=True)

        with tab2:
            st.subheader("🛒 Sales Performance")
            if 'salesman' in df_filtered:
                chart_sales = df_filtered.groupby('salesman')['volume'].sum().reset_index().sort_values(by='volume', ascending=False)
                fig_sales = px.bar(chart_sales, x='salesman', y='volume', title="Total Volume per Salesman")
                st.plotly_chart(fig_sales, use_container_width=True)

            if 'end customer name' in df_filtered:
                chart_cust = df_filtered.groupby('end customer name')['volume'].sum().reset_index().sort_values(by='volume', ascending=False)
                fig_cust = px.bar(chart_cust, x='end customer name', y='volume', title="Total Volume per End Customer Name")
                st.plotly_chart(fig_cust, use_container_width=True)

        # =========================
        # Export
        # =========================
        if st.button("📥 Export ke Excel"):
            export_file = "dashboard_export.xlsx"
            df_filtered.to_excel(export_file, index=False)
            st.success("✅ Data berhasil diexport ke Excel!")
            st.download_button("Download File", data=open(export_file, 'rb').read(), file_name=export_file)
