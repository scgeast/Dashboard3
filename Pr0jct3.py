import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# Halaman & Tema
# =========================
st.set_page_config(page_title="📦 Dashboard Analyst Delivery & Sales", layout="wide")
color_palette = ["#00FFFF", "#8A2BE2", "#00FF00", "#FF00FF", "#FFD700"]

# =========================
# Upload Data
# =========================
uploaded_file = st.file_uploader("Upload File Excel", type=["xlsx"])
if uploaded_file:
    df = pd.ExcelFile(uploaded_file).parse("Data")

    # Pastikan kolom sesuai
    df["Tanggal Pengiriman"] = pd.to_datetime(df["Tanggal Pengiriman"])
    df["Ritase"] = 1  # setiap DP No dianggap 1 trip
    df["Volume"] = df["Qty"]  # asumsi volume = Qty

    # Filter berdasarkan tanggal
    min_date, max_date = df["Tanggal Pengiriman"].min(), df["Tanggal Pengiriman"].max()
    date_range = st.date_input("Pilih Rentang Tanggal", [min_date, max_date])
    df_filtered = df[(df["Tanggal Pengiriman"] >= pd.to_datetime(date_range[0])) &
                     (df["Tanggal Pengiriman"] <= pd.to_datetime(date_range[1]))]
    num_days = (pd.to_datetime(date_range[1]) - pd.to_datetime(date_range[0])).days + 1

    # =========================
    # 1. Dashboard Summary
    # =========================
    st.markdown("<h2>📊 Summarize</h2>", unsafe_allow_html=True)

    total_ritase = int(df_filtered["Ritase"].sum())
    total_volume = int(df_filtered["Volume"].sum())
    total_truck = df_filtered["Truck No"].nunique()
    total_sales = df_filtered["Salesman"].nunique()
    total_customer = df_filtered["End Customer Name"].nunique()
    avg_volume_per_day = int(total_volume / num_days)

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("🚚 Total Ritase", f"{total_ritase}")
    col2.metric("📦 Total Volume", f"{total_volume}")
    col3.metric("🚛 Total Truck", f"{total_truck}")
    col4.metric("🧑‍💼 Salesman", f"{total_sales}")
    col5.metric("👥 Customers", f"{total_customer}")
    col6.metric("📊 Avg Volume/Day", f"{avg_volume_per_day}")

    # =========================
    # 2. Perform Volume per Day
    # =========================
    st.markdown("<h2>📈 Perform Volume per Day</h2>", unsafe_allow_html=True)
    perf_day = df_filtered.groupby("Tanggal Pengiriman")[["Ritase", "Volume"]].sum().reset_index()

    fig_perf_day = px.bar(perf_day, x="Tanggal Pengiriman", y="Volume", text="Volume",
                          color_discrete_sequence=color_palette, title="Volume per Day")
    fig_perf_day.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(fig_perf_day, use_container_width=True)

    fig_perf_ritase = px.line(perf_day, x="Tanggal Pengiriman", y="Ritase", markers=True,
                              color_discrete_sequence=color_palette, title="Ritase per Day")
    st.plotly_chart(fig_perf_ritase, use_container_width=True)

    # =========================
    # 3. Delivery Performance
    # =========================
    st.markdown("<h2>🚚 Delivery Performance</h2>", unsafe_allow_html=True)
    delivery_perf = df_filtered.groupby("Tanggal Pengiriman")[["Ritase", "Volume"]].sum().reset_index()

    fig_delivery = px.line(delivery_perf, x="Tanggal Pengiriman", y=["Ritase", "Volume"],
                           markers=True, title="Trend Delivery Performance",
                           color_discrete_sequence=color_palette)
    st.plotly_chart(fig_delivery, use_container_width=True)

    # =========================
    # 4. Truck Utilization
    # =========================
    st.markdown("<h2>🚛 Truck Utilization</h2>", unsafe_allow_html=True)

    total_trip = df_filtered.groupby("Truck No")["Ritase"].sum().reset_index(name="Total Trip")
    total_vol_truck = df_filtered.groupby("Truck No")["Volume"].sum().reset_index(name="Total Volume")
    truck_stats = pd.merge(total_trip, total_vol_truck, on="Truck No", how="outer")

    truck_stats["Avg Trip per Truck (per Day)"] = (truck_stats["Total Trip"] / num_days).round(0).astype(int)
    truck_stats["Avg Load per Trip"] = (truck_stats["Total Volume"] / truck_stats["Total Trip"]).round(0).astype(int)

    fig_trip = px.bar(truck_stats, x="Truck No", y="Total Trip", text="Total Trip",
                      color="Truck No", color_discrete_sequence=color_palette,
                      title="Total Trip per Truck")
    fig_trip.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(fig_trip, use_container_width=True)

    fig_avg_trip = px.bar(truck_stats, x="Truck No", y="Avg Trip per Truck (per Day)",
                          text="Avg Trip per Truck (per Day)", color="Truck No",
                          color_discrete_sequence=color_palette,
                          title=f"Avg Trip per Truck per Day (Total Trip ÷ {num_days} hari)")
    fig_avg_trip.update_traces(texttemplate="%{text:.0f}", textposition="outside", cliponaxis=False)
    st.plotly_chart(fig_avg_trip, use_container_width=True)

    fig_avg_load = px.bar(truck_stats, x="Truck No", y="Avg Load per Trip",
                          text="Avg Load per Trip", color="Truck No",
                          color_discrete_sequence=color_palette,
                          title="Avg Load per Trip (Total Volume ÷ Total Trip)")
    fig_avg_load.update_traces(texttemplate="%{text:.0f}", textposition="outside", cliponaxis=False)
    st.plotly_chart(fig_avg_load, use_container_width=True)

    # =========================
    # 5. Distance Analysis
    # =========================
    st.markdown("<h2>📍 Distance Analysis</h2>", unsafe_allow_html=True)

    dist_area = df_filtered.groupby("Area")["Distance"].sum().reset_index(name="Total Distance")
    avg_dist_area = df_filtered.groupby("Area")["Distance"].mean().reset_index(name="Avg Distance")
    avg_dist_area["Avg Distance"] = avg_dist_area["Avg Distance"].round(0).astype(int)

    fig_total_dist = px.bar(dist_area, x="Area", y="Total Distance", text="Total Distance",
                            color="Area", color_discrete_sequence=color_palette,
                            title="Total Distance per Area")
    fig_total_dist.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(fig_total_dist, use_container_width=True)

    fig_avg_dist = px.bar(avg_dist_area, x="Area", y="Avg Distance", text="Avg Distance",
                          color="Area", color_discrete_sequence=color_palette,
                          title="Avg Distance per Area (per Trip)")
    fig_avg_dist.update_traces(texttemplate="%{text:.0f}", textposition="outside", cliponaxis=False)
    st.plotly_chart(fig_avg_dist, use_container_width=True)

    # =========================
    # 6. Sales & Customer Performance
    # =========================
    st.markdown("<h2>🛒 Sales & Customer Performance</h2>", unsafe_allow_html=True)

    sales_perf = df_filtered.groupby("Salesman")["Volume"].sum().reset_index().sort_values(by="Volume", ascending=False)
    fig_sales = px.bar(sales_perf, x="Salesman", y="Volume", text="Volume",
                       color="Salesman", color_discrete_sequence=color_palette,
                       title="Volume per Salesman")
    fig_sales.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(fig_sales, use_container_width=True)

    cust_perf = df_filtered.groupby("End Customer Name")["Volume"].sum().reset_index().sort_values(by="Volume", ascending=False)
    fig_cust = px.bar(cust_perf, x="End Customer Name", y="Volume", text="Volume",
                      color="End Customer Name", color_discrete_sequence=color_palette,
                      title="Volume per Customer")
    fig_cust.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(fig_cust, use_container_width=True)
