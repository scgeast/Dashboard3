# Dashboard3
import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# Konfigurasi halaman
# =========================
st.set_page_config(
    page_title="📦 Dashboard Analyst Delivery & Sales",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# Tema & Warna
# =========================
color_palette = ["#00FFFF", "#8A2BE2", "#00FF00", "#FF00FF", "#FFD700", "#00CED1"]

# Sidebar theme pilihan
theme = st.sidebar.radio("🎨 Pilih Tema", ["Gelap", "Terang"])
bg_color = "#0d0f15" if theme == "Gelap" else "#fff"
font_color = "white" if theme == "Gelap" else "black"
card_bg = "#1f1f1f" if theme == "Gelap" else "#f5f5f5"

# =========================
# Custom CSS untuk styling mirip Power BI
# =========================
st.markdown(f"""
<style>
    /* Reset scrollbar style for better UX */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    ::-webkit-scrollbar-thumb {{
        background-color: #888;
        border-radius: 10px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: #555;
    }}

    /* Header styling */
    .dashboard-header {{
        font-size: 32px;
        font-weight: 700;
        color: {font_color};
        margin-bottom: 0;
        padding-bottom: 0;
        border-bottom: 3px solid {color_palette[1]};
    }}

    /* Card style */
    .metric-card {{
        background-color: {card_bg};
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        color: {font_color};
        box-shadow: 0 3px 6px rgba(0,0,0,0.3);
        transition: background-color 0.3s ease;
    }}
    .metric-card:hover {{
        background-color: {color_palette[0]};
        color: #000;
        cursor: default;
    }}
    .metric-label {{
        font-size: 16px;
        margin-bottom: 5px;
        opacity: 0.8;
    }}
    .metric-value {{
        font-size: 28px;
        font-weight: 700;
    }}

    /* Sidebar styling */
    .sidebar .sidebar-content {{
        background-color: {bg_color};
        color: {font_color};
        padding-top: 20px;
    }}

    /* Filter label styling */
    .stSidebar label {{
        font-weight: 600;
        color: {font_color} !important;
    }}

</style>
""", unsafe_allow_html=True)

# =========================
# Header
# =========================
st.markdown(f"<h1 class='dashboard-header'>📦 Dashboard Analyst Delivery dan Sales</h1>", unsafe_allow_html=True)

# =========================
# Upload File
# =========================
uploaded_file = st.sidebar.file_uploader("📥 Upload file Excel (5MB–30MB)", type=["xlsx", "xls"])

if not uploaded_file:
    st.info("Silakan upload file Excel di sidebar untuk memulai analisis.")
    st.stop()

# =========================
# Load Data
# =========================
df = pd.read_excel(uploaded_file)
df.columns = df.columns.str.strip()

rename_map = {
    "Tanggal P": "Tanggal Pengiriman",
    # Other renames if necessary
}
df.rename(columns=rename_map, inplace=True)

# Add missing columns default values
for col in ["Salesman", "End Customer", "Volume", "Truck No", "Distance", "Ritase", "Area", "Plant Name"]:
    if col not in df.columns:
        df[col] = 1 if col in ["Volume", "Ritase", "Distance"] else "Unknown"

df["Tanggal Pengiriman"] = pd.to_datetime(df["Tanggal Pengiriman"], errors='coerce')
df.dropna(subset=["Tanggal Pengiriman"], inplace=True)

# =========================
# Sidebar Filters
# =========================
st.sidebar.header("🔎 Filter Data")

min_date = df["Tanggal Pengiriman"].min()
max_date = df["Tanggal Pengiriman"].max()

start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

area_options = df["Area"].dropna().unique()
area_selected = st.sidebar.multiselect("Area", options=area_options, default=area_options)

plant_options = df[df["Area"].isin(area_selected)]["Plant Name"].dropna().unique() if area_selected else df["Plant Name"].dropna().unique()
plant_selected = st.sidebar.multiselect("Plant Name", options=plant_options, default=plant_options)

salesman_options = df["Salesman"].dropna().unique()
salesman_selected = st.sidebar.multiselect("Salesman", options=salesman_options, default=salesman_options)

customer_options = df["End Customer"].dropna().unique()
customer_selected = st.sidebar.multiselect("End Customer", options=customer_options, default=customer_options)

if st.sidebar.button("🔄 Reset Filter"):
    st.experimental_rerun()

# =========================
# Filter DataFrame
# =========================
df_filtered = df[
    (df["Tanggal Pengiriman"] >= pd.to_datetime(start_date)) &
    (df["Tanggal Pengiriman"] <= pd.to_datetime(end_date)) &
    (df["Area"].isin(area_selected)) &
    (df["Plant Name"].isin(plant_selected)) &
    (df["Salesman"].isin(salesman_selected)) &
    (df["End Customer"].isin(customer_selected))
]

# =========================
# Metrics Summary
# =========================
st.markdown("### 📊 Summary Metrics")
cols = st.columns(6)

def metric_card(label, value, idx):
    with cols[idx]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)

metric_card("Total Area", df_filtered["Area"].nunique(), 0)
metric_card("Total Plant", df_filtered["Plant Name"].nunique(), 1)
metric_card("Total Volume", f"{df_filtered['Volume'].sum():,.2f}", 2)
metric_card("Total Ritase", f"{df_filtered['Ritase'].sum():,.2f}", 3)
metric_card("Total End Customer", df_filtered["End Customer"].nunique(), 4)
metric_card("Total Truck Mixer", df_filtered["Truck No"].nunique(), 5)

# =========================
# Visualisasi Volume Per Day
# =========================
st.markdown("---")
st.markdown(f"## 📈 Volume Per Day")

volume_daily = df_filtered.groupby("Tanggal Pengiriman")["Volume"].sum().reset_index()
volume_daily["Volume"] = volume_daily["Volume"].round(2)

fig_volume = px.line(volume_daily, x="Tanggal Pengiriman", y="Volume", markers=True,
                     text=volume_daily["Volume"], title="Volume Per Day",
                     color_discrete_sequence=[color_palette[1]])
fig_volume.update_traces(textposition="top center")
fig_volume.update_layout(
    plot_bgcolor=bg_color,
    paper_bgcolor=bg_color,
    font=dict(color=font_color),
    xaxis=dict(tickangle=45),
    height=400,
)

st.plotly_chart(fig_volume, use_container_width=True)

# =========================
# Delivery Performance per Area & Plant
# =========================
st.markdown("---")
st.markdown("## 🚚 Perform Delivery")

col1, col2 = st.columns(2)

with col1:
    volume_area = df_filtered.groupby("Area")["Volume"].sum().reset_index().sort_values(by="Volume", ascending=False)
    fig_area = px.bar(volume_area, x="Area", y="Volume", text="Volume", color="Area",
                      color_discrete_sequence=color_palette, title="Perform Delivery per Area")
    fig_area.update_layout(
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=font_color),
        height=400,
        showlegend=False,
    )
    st.plotly_chart(fig_area, use_container_width=True)

with col2:
    volume_plant = df_filtered.groupby("Plant Name")["Volume"].sum().reset_index().sort_values(by="Volume", ascending=False)
    fig_plant = px.bar(volume_plant, x="Plant Name", y="Volume", text="Volume", color="Plant Name",
                       color_discrete_sequence=color_palette, title="Perform Delivery per Plant")
    fig_plant.update_layout(
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=font_color),
        height=400,
        showlegend=False,
    )
    st.plotly_chart(fig_plant, use_container_width=True)

# =========================
# Performa Sales & Customer
# =========================
st.markdown("---")
st.markdown("## 👤 Performa Sales & Customer")

col3, col4 = st.columns(2)

with col3:
    sales_perf = df_filtered.groupby("Salesman")["Volume"].sum().reset_index().sort_values(by="Volume", ascending=False)
    fig_salesman = px.bar(sales_perf, x="Salesman", y="Volume", text="Volume", color="Salesman",
                          color_discrete_sequence=color_palette, title="Performa Salesman")
    fig_salesman.update_layout(
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=font_color),
        height=500,
        showlegend=False,
    )
    st.plotly_chart(fig_salesman, use_container_width=True)

with col4:
    cust_perf = df_filtered.groupby("End Customer")["Volume"].sum().reset_index().sort_values(by="Volume", ascending=False)
    fig_customer = px.bar(cust_perf, x="End Customer", y="Volume", text="Volume", color="End Customer",
                          color_discrete_sequence=color_palette, title="Performa End Customer")
    fig_customer.update_layout(
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=font_color),
        height=500,
        showlegend=False,
    )
    st.plotly_chart(fig_customer, use_container_width=True)

# =========================
# Utilisasi Truck Mixer
# =========================
st.markdown("---")
st.markdown("## 🚛 Utilisasi Truck Mixer")

ritase_truck = df_filtered.groupby("Truck No")["Ritase"].sum().reset_index().sort_values(by="Ritase", ascending=False)
fig_truck_total = px.bar(ritase_truck, x="Truck No", y="Ritase", text="Ritase", color="Truck No",
                         color_discrete_sequence=color_palette, title="Total Ritase per Truck")
fig_truck_total.update_layout(
    plot_bgcolor=bg_color,
    paper_bgcolor=bg_color,
    font=dict(color=font_color),
    height=400,
    showlegend=False,
)
st.plotly_chart(fig_truck_total, use_container_width=True)

volume_avg = df_filtered.groupby("Truck No")["Volume"].mean().reset_index().sort_values(by="Volume", ascending=False)
fig_truck_avg = px.bar(volume_avg, x="Truck No", y="Volume", text="Volume", color="Truck No",
                       color_discrete_sequence=color_palette, title="Average Volume per Ritase (Truck)")
fig_truck_avg.update_layout(
    plot_bgcolor=bg_color,
    paper_bgcolor=bg_color,
    font=dict(color=font_color),
    height=400,
    showlegend=False,
)
st.plotly_chart(fig_truck_avg, use_container_width=True)

# =========================
# Tren & Analisa Jarak Tempuh
# =========================
st.markdown("---")
st.markdown("## 📈 Visualisasi Tren")

trend_ritase = df_filtered.groupby("Tanggal Pengiriman")["Ritase"].sum().reset_index()
trend_ritase["Ritase"] = trend_ritase["Ritase"].round(2)
fig_trend_ritase = px.line(trend_ritase, x="Tanggal Pengiriman", y="Ritase", markers=True, text="Ritase", title="Tren Ritase")
fig_trend_ritase.update_layout(
    plot_bgcolor=bg_color,
    paper_bgcolor=bg_color,
    font=dict(color=font_color),
    height=400,
)
st.plotly_chart(fig_trend_ritase, use_container_width=True)

trend_volume = df_filtered.groupby("Tanggal Pengiriman")["Volume"].sum().reset_index()
trend_volume["Volume"] = trend_volume["Volume"].round(2)
fig_trend_volume = px.line(trend_volume, x="Tanggal Pengiriman", y="Volume", markers=True, text="Volume", title="Tren Volume")
fig_trend_volume.update_layout(
    plot_bgcolor=bg_color,
    paper_bgcolor=bg_color,
    font=dict(color=font_color),
    height=400,
)
st.plotly_chart(fig_trend_volume, use_container_width=True)

st.markdown("## 📍 Analisa Jarak Tempuh")
col5, col6 = st.columns(2)
with col5:
    avg_dist_plant = df_filtered.groupby("Plant Name")["Distance"].mean().reset_index()
    avg_dist_plant["Distance"] = avg_dist_plant["Distance"].round(2)
    fig_avg_dist_plant = px.bar(avg_dist_plant, x="Plant Name", y="Distance", text="Distance", title="Average Distance per Plant")
    fig_avg_dist_plant.update_layout(
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=font_color),
        height=400,
        showlegend=False,
    )
    st.plotly_chart(fig_avg_dist_plant, use_container_width=True)

with col6:
    avg_dist_area = df_filtered.groupby("Area")["Distance"].mean().reset_index()
    avg_dist_area["Distance"] = avg_dist_area["Distance"].round(2)
    fig_avg_dist_area = px.bar(avg_dist_area, x="Area", y="Distance", text="Distance", title="Average Distance per Area")
    fig_avg_dist_area.update_layout(
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=font_color),
        height=400,
        showlegend=False,
    )
    st.plotly_chart(fig_avg_dist_area, use_container_width=True)
