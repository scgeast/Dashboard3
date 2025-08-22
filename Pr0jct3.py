import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# Konfigurasi halaman
# =========================
st.set_page_config(page_title="📦 Dashboard Analyst Delivery & Sales", layout="wide")

# =========================
# Warna & CSS Tema Futuristik
# =========================
color_palette = ["#00FFFF", "#8A2BE2", "#00FF00", "#FF00FF", "#FFD700", "#00CED1"]

theme = st.sidebar.radio("🎨 Pilih Tema", ["Gelap", "Terang"])
bg_color = "#0d0f15" if theme == "Gelap" else "#f0f2f6"
font_color = "#00FFFF" if theme == "Gelap" else "#003366"
box_bg = "#121526" if theme == "Gelap" else "#e1e5f2"

# =========================
# CSS Kustom
# =========================
st.markdown(f"""
    <style>
    body {{
        background-color: {bg_color};
        color: {font_color};
    }}
    h1, h2, h3, h4 {{
        color: {font_color};
        text-shadow: 0 0 10px {font_color};
    }}
    .metric-box {{
        background-color: {box_bg};
        border: 2px solid {font_color};
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 20px {font_color};
        transition: transform 0.3s ease;
    }}
    .metric-box:hover {{
        transform: scale(1.05);
        box-shadow: 0 0 30px #FF00FF, 0 0 20px {font_color};
    }}
    .metric-label {{
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: 8px;
        color: {font_color};
    }}
    .metric-value {{
        font-size: 2rem;
        font-weight: 900;
        color: {font_color};
        text-shadow: 0 0 5px #00FFFF;
    }}
    div.stButton > button {{
        background-color: {font_color} !important;
        color: {bg_color} !important;
        font-weight: 700;
        border-radius: 10px;
        box-shadow: 0 0 10px {font_color};
    }}
    div.stButton > button:hover {{
        background-color: #FF00FF !important;
        color: white !important;
        box-shadow: 0 0 20px #FF00FF;
    }}
    </style>
""", unsafe_allow_html=True)

# =========================
# Judul
# =========================
st.markdown(f"<h1 style='text-align:center;'>📦 Dashboard Analyst Delivery dan Sales</h1>", unsafe_allow_html=True)

# =========================
# Upload File
# =========================
uploaded_file = st.file_uploader("📂 Upload file Excel (5MB–30MB)", type=["xlsx", "xls"])

# =========================
# Fungsi Styling Chart
# =========================
def styled_chart(fig, height=None, font_size=12, margin=None, text_format=".2f", text_position="outside", show_legend=False, title_font_size=18):
    fig.update_layout(
        plot_bgcolor=box_bg,
        paper_bgcolor=box_bg,
        font=dict(color=font_color, size=font_size),
        title_font=dict(color=font_color, size=title_font_size),
        xaxis=dict(tickangle=45, gridcolor='#222244'),
        yaxis=dict(gridcolor='#222244'),
        showlegend=show_legend
    )
    if height:
        fig.update_layout(height=height)
    if margin:
        fig.update_layout(margin=margin)
    try:
        fig.update_traces(texttemplate=f"%{{text:{text_format}}}", textposition=text_position)
    except Exception:
        pass
    return fig

# =========================
# Fungsi Kotak Metric
# =========================
def boxed_metric(label, value):
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)

# =========================
# Fungsi Volume Chart
# =========================
def render_volume_chart(df_filtered):
    st.markdown(f"<h2>📈 Volume Per Day</h2>", unsafe_allow_html=True)
    sales_trend = df_filtered.groupby("Tanggal Pengiriman")["Volume"].sum().reset_index()
    sales_trend["Volume"] = sales_trend["Volume"].round(2)
    fig = px.line(sales_trend, x="Tanggal Pengiriman", y="Volume", text="Volume", title="Volume Per Day")
    fig.update_traces(mode="lines+markers+text", textposition="top center")
    st.plotly_chart(styled_chart(fig, height=400, font_size=13), use_container_width=True)

# =========================
# MAIN APP
# =========================
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    # Rename kolom jika perlu
    rename_map = {
        "Tanggal P": "Tanggal Pengiriman",
        "Plant Name": "Plant Name",
        "Area": "Area",
        "Ritase": "Ritase"
    }
    df.rename(columns=rename_map, inplace=True)

    # Tambah kolom default
    for col in ["Salesman", "End Customer", "Volume", "Truck No", "Distance", "Ritase"]:
        if col not in df.columns:
            df[col] = 1 if col in ["Volume", "Ritase", "Distance"] else "Unknown"

    df["Tanggal Pengiriman"] = pd.to_datetime(df["Tanggal Pengiriman"])

    # =========================
    # Sidebar Filter
    # =========================
    st.sidebar.header("🔎 Filter Data")
    start_date = st.sidebar.date_input("Start Date", df["Tanggal Pengiriman"].min())
    end_date = st.sidebar.date_input("End Date", df["Tanggal Pengiriman"].max())
    area = st.sidebar.multiselect("Area", options=df["Area"].dropna().unique())
    plant_options = df[df["Area"].isin(area)]["Plant Name"].dropna().unique() if area else df["Plant Name"].dropna().unique()
    plant = st.sidebar.multiselect("Plant Name", options=plant_options)
    salesman = st.sidebar.multiselect("Salesman", options=df["Salesman"].dropna().unique())
    end_customer = st.sidebar.multiselect("End Customer", options=df["End Customer"].dropna().unique())

    if st.sidebar.button("🔄 Reset Filter"):
        st.experimental_rerun()

    # Filter Data
    df_filtered = df[
        (df["Tanggal Pengiriman"] >= pd.to_datetime(start_date)) &
        (df["Tanggal Pengiriman"] <= pd.to_datetime(end_date))
    ]
    if area:
        df_filtered = df_filtered[df_filtered["Area"].isin(area)]
    if plant:
        df_filtered = df_filtered[df_filtered["Plant Name"].isin(plant)]
    if salesman:
        df_filtered = df_filtered[df_filtered["Salesman"].isin(salesman)]
    if end_customer:
        df_filtered = df_filtered[df_filtered["End Customer"].isin(end_customer)]

    # =========================
    # Summary Metrics
    # =========================
    st.markdown(f"<h2>📊 Summary</h2>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        boxed_metric("Total Area", df_filtered["Area"].nunique())
    with col2:
        boxed_metric("Total Plant", df_filtered["Plant Name"].nunique())
    with col3:
        boxed_metric("Total Volume", f"{df_filtered['Volume'].sum():,.2f}")
    with col4:
        boxed_metric("Total Ritase", f"{df_filtered['Ritase'].sum():,.2f}")
    with col5:
        boxed_metric("End Customer", df_filtered["End Customer"].nunique())
    with col6:
        boxed_metric("Truck Mixer", df_filtered["Truck No"].nunique())

    # =========================
    # Volume Chart
    # =========================
    render_volume_chart(df_filtered)

    # =========================
    # Delivery Performance
    # =========================
    st.subheader("🚚 Perform Delivery per Area & Plant")
    col7, col8 = st.columns(2)

    with col7:
        volume_area = df_filtered.groupby("Area")["Volume"].sum().reset_index().sort_values(by="Volume", ascending=False)
        fig_area = px.bar(volume_area, x="Area", y="Volume", text="Volume", color="Area",
                          title="Volume per Area", color_discrete_sequence=color_palette)
        st.plotly_chart(styled_chart(fig_area), use_container_width=True)

    with col8:
        volume_plant = df_filtered.groupby("Plant Name")["Volume"].sum().reset_index().sort_values(by="Volume", ascending=False)
        fig_plant = px.bar(volume_plant, x="Plant Name", y="Volume", text="Volume", color="Plant Name",
                           title="Volume per Plant", color_discrete_sequence=color_palette)
        st.plotly_chart(styled_chart(fig_plant), use_container_width=True)

    # =========================
    # Salesman & Customer
    # =========================
    st.subheader("👤 Performa Sales & Customer")
    sales_perf = df_filtered.groupby("Salesman")["Volume"].sum().reset_index().sort_values(by="Volume", ascending=False)
    fig_salesman = px.bar(sales_perf, x="Salesman", y="Volume", text="Volume", color="Salesman",
                          title="Salesman Performance", color_discrete_sequence=color_palette)
    st.plotly_chart(styled_chart(fig_salesman, height=500), use_container_width=True)

    cust_perf = df_filtered.groupby("End Customer")["Volume"].sum().reset_index().sort_values(by="Volume", ascending=False)
    fig_customer = px.bar(cust_perf, x="End Customer", y="Volume", text="Volume", color="End Customer",
                          title="Customer Performance", color_discrete_sequence=color_palette)
    st.plotly_chart(styled_chart(fig_customer, height=500), use_container_width=True)

    # =========================
    # Truck Utilization
    # =========================
    st.subheader("🚛 Truck Mixer Utilization")
    ritase_truck = df_filtered.groupby("Truck No")["Ritase"].sum().reset_index().sort_values(by="Ritase", ascending=False)
    fig_ritase = px.bar(ritase_truck, x="Truck No", y="Ritase", text="Ritase", color="Truck No",
                        title="Ritase per Truck", color_discrete_sequence=color_palette)
    st.plotly_chart(styled_chart(fig_ritase), use_container_width=True)

    volume_avg = df_filtered.groupby("Truck No")["Volume"].mean().reset_index().sort_values(by="Volume", ascending=False)
    fig_avg = px.bar(volume_avg, x="Truck No", y="Volume", text="Volume", color="Truck No",
                     title="Avg Volume per Ritase", color_discrete_sequence=color_palette)
    st.plotly_chart(styled_chart(fig_avg), use_container_width=True)

    # =========================
    # Trend Visual & Distance
    # =========================
    st.subheader("📈 Trend Volume & Ritase")
    trend_ritase = df_filtered.groupby("Tanggal Pengiriman")["Ritase"].sum().reset_index()
    fig_trend_ritase = px.line(trend_ritase, x="Tanggal Pengiriman", y="Ritase", text="Ritase", markers=True, title="Trend Ritase")
    st.plotly_chart(styled_chart(fig_trend_ritase), use_container_width=True)

    trend_volume = df_filtered.groupby("Tanggal Pengiriman")["Volume"].sum().reset_index()
    fig_trend_volume = px.line(trend_volume, x="Tanggal Pengiriman", y="Volume", text="Volume", markers=True, title="Trend Volume")
    st.plotly_chart(styled_chart(fig_trend_volume), use_container_width=True)

    st.subheader("📍 Distance Analysis")
    col9, col10 = st.columns(2)
    with col9:
        avg_dist_plant = df_filtered.groupby("Plant Name")["Distance"].mean().reset_index()
        fig_avg_plant = px.bar(avg_dist_plant, x="Plant Name", y="Distance", text="Distance", title="Avg Distance per Plant")
        st.plotly_chart(styled_chart(fig_avg_plant), use_container_width=True)

    with col10:
        avg_dist_area = df_filtered.groupby("Area")["Distance"].mean().reset_index()
        fig_avg_area = px.bar(avg_dist_area, x="Area", y="Distance", text="Distance", title="Avg Distance per Area")
        st.plotly_chart(styled_chart(fig_avg_area), use_container_width=True)

else:
    st.info("📤 Silakan upload file Excel terlebih dahulu untuk menampilkan dashboard.")


Tes 3 tampilan power bi
