import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# Config halaman & tema
# =========================
st.set_page_config(page_title="📦 Dashboard Analyst Delivery & Sales", layout="wide")
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
body {{background-color: {bg_color}; color: {font_color};}}
h1,h2,h3,h4 {{color: {font_color}; text-shadow: 0 0 10px {font_color};}}
.metric-box {{background-color: {box_bg}; border:2px solid {font_color}; border-radius:15px;
padding:20px;text-align:center;box-shadow:0 0 20px {font_color}; transition: transform 0.3s;}}
.metric-box:hover {{transform:scale(1.05); box-shadow:0 0 30px #FF00FF,0 0 20px {font_color};}}
.metric-label {{font-weight:700;font-size:1.2rem;margin-bottom:8px;color:{font_color};}}
.metric-value {{font-size:2rem;font-weight:900;color:{font_color};text-shadow:0 0 5px #00FFFF;}}
div.stButton>button {{background-color:{font_color} !important;color:{bg_color} !important;
font-weight:700;border-radius:10px;box-shadow:0 0 10px {font_color};}}
div.stButton>button:hover {{background-color:#FF00FF !important;color:white !important;
box-shadow:0 0 20px #FF00FF;}}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>📦 Dashboard Analyst Delivery & Sales</h1>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("📂 Upload file Excel (5MB–30MB)", type=["xlsx","xls"])

# =========================
# Fungsi chart & metric
# =========================
def styled_chart(fig, height=None, font_size=12, margin=None, text_format=".2f", text_position="outside", show_legend=False, title_font_size=18):
    fig.update_layout(plot_bgcolor=box_bg, paper_bgcolor=box_bg,
                      font=dict(color=font_color,size=font_size),
                      title_font=dict(color=font_color,size=title_font_size),
                      xaxis=dict(tickangle=45,gridcolor='#222244'),
                      yaxis=dict(gridcolor='#222244'), showlegend=show_legend)
    if height: fig.update_layout(height=height)
    if margin: fig.update_layout(margin=margin)
    try: fig.update_traces(texttemplate=f"%{{text:{text_format}}}", textposition=text_position, cliponaxis=False)
    except: pass
    return fig

def boxed_metric(label,value):
    st.markdown(f"<div class='metric-box'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div></div>", unsafe_allow_html=True)

# =========================
# MAIN APP
# =========================
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    # -------------------------
    # Pemetaan kolom fleksibel
    # -------------------------
    column_mapping = {
        "Dp Date": ["Tanggal P","Dp Date","Delivery Date","DP Date"],
        "Sales Man": ["Salesman","Sales Man"],
        "Area": ["Area","Region","Zona"],
        "Plant Name": ["Plant Name","Plant","Factory"],
        "End Customer Name": ["End Customer","Customer","Buyer","End Customer Name"],
        "End Customer No": ["End Customer No","Customer No","Buyer No"],
        "Volume": ["Volume","Qty","Quantity"],
        "Ritase": ["Ritase","Trips"],
        "Truck No": ["Truck No","Truck Number","Vehicle"],
        "Distance": ["Distance","Km","Jarak"]
    }

    for target_col, alternatives in column_mapping.items():
        found_col = next((c for c in alternatives if c in df.columns), None)
        if found_col: df.rename(columns={found_col: target_col}, inplace=True)
        else:
            df[target_col] = 1 if target_col in ["Volume","Ritase","Distance"] else "Unknown"

    df["Dp Date"] = pd.to_datetime(df["Dp Date"], errors='coerce')

    # =========================
    # Sidebar Filter
    # =========================
    st.sidebar.header("🔎 Filter Data")
    start_date = st.sidebar.date_input("Start Date", df["Dp Date"].min())
    end_date = st.sidebar.date_input("End Date", df["Dp Date"].max())
    area = st.sidebar.multiselect("Area", options=df["Area"].dropna().unique())
    plant_options = df[df["Area"].isin(area)]["Plant Name"].dropna().unique() if area else df["Plant Name"].dropna().unique()
    plant = st.sidebar.multiselect("Plant Name", options=plant_options)
    salesman = st.sidebar.multiselect("Sales Man", options=df["Sales Man"].dropna().unique())
    end_customer = st.sidebar.multiselect("End Customer Name", options=df["End Customer Name"].dropna().unique())
    if st.sidebar.button("🔄 Reset Filter"): st.experimental_rerun()

    df_filtered = df[(df["Dp Date"]>=pd.to_datetime(start_date)) & (df["Dp Date"]<=pd.to_datetime(end_date))]
    if area: df_filtered = df_filtered[df_filtered["Area"].isin(area)]
    if plant: df_filtered = df_filtered[df_filtered["Plant Name"].isin(plant)]
    if salesman: df_filtered = df_filtered[df_filtered["Sales Man"].isin(salesman)]
    if end_customer: df_filtered = df_filtered[df_filtered["End Customer Name"].isin(end_customer)]

    # =========================
    # 1. Summary Metrics
    # =========================
    st.markdown("<h2>📊 Summary</h2>", unsafe_allow_html=True)
    cols = st.columns(5)
    with cols[0]: boxed_metric("Total Area", df_filtered["Area"].nunique())
    with cols[1]: boxed_metric("Total Plant", df_filtered["Plant Name"].nunique())
    with cols[2]: boxed_metric("Total Volume", f"{df_filtered['Volume'].sum():,.2f}")
    with cols[3]: boxed_metric("Total Ritase", f"{df_filtered['Ritase'].sum():,.2f}")
    with cols[4]: boxed_metric("Truck Mixer", df_filtered["Truck No"].nunique())

    # =========================
    # 2. Volume Per Day
    # =========================
    st.markdown("<h2>📈 Volume Per Day</h2>", unsafe_allow_html=True)
    sales_trend = df_filtered.groupby("Dp Date")["Volume"].sum().reset_index()
    fig_vol_day = px.line(sales_trend, x="Dp Date", y="Volume", markers=True, text="Volume", title="Volume Per Day")
    fig_vol_day.update_traces(textposition="top center", textfont=dict(size=11))
    st.plotly_chart(styled_chart(fig_vol_day, height=400), use_container_width=True)

    # =========================
    # 3. Delivery Performance
    # =========================
    st.subheader("🚚 Delivery Performance")
    col_area, col_plant = st.columns(2)
    with col_area:
        vol_area = df_filtered.groupby("Area")["Volume"].sum().reset_index().sort_values("Volume", ascending=False)
        fig_area = px.bar(vol_area, x="Area", y="Volume", text="Volume", color="Area",
                          color_discrete_sequence=color_palette, title="Total Volume per Area")
        fig_area.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(styled_chart(fig_area), use_container_width=True)
    with col_plant:
        vol_plant = df_filtered.groupby("Plant Name")["Volume"].sum().reset_index().sort_values("Volume", ascending=False)
        fig_plant = px.bar(vol_plant, x="Plant Name", y="Volume", text="Volume", color="Plant Name",
                           color_discrete_sequence=color_palette, title="Total Volume per Plant")
        fig_plant.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(styled_chart(fig_plant), use_container_width=True)

    # =========================
    # 4. Truck Utilization (FULL WIDTH)
    # =========================
    st.markdown("<hr><h2>🚛 Truck Utilization</h2>", unsafe_allow_html=True)
    ritase_truck = df_filtered.groupby("Truck No")["Ritase"].sum().reset_index().sort_values("Ritase", ascending=False)
    fig_rit = px.bar(ritase_truck, x="Truck No", y="Ritase", text="Ritase", color="Truck No",
                     color_discrete_sequence=color_palette, title="Total Trip per Truck")
    fig_rit.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(styled_chart(fig_rit), use_container_width=True)

    avg_rit = df_filtered.groupby("Truck No")["Ritase"].mean().reset_index()
    fig_avg_rit = px.bar(avg_rit, x="Truck No", y="Ritase", text="Ritase", color="Truck No",
                         color_discrete_sequence=color_palette, title="Avg Trip per Truck")
    fig_avg_rit.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(styled_chart(fig_avg_rit), use_container_width=True)

    avg_load = df_filtered.groupby("Truck No")["Volume"].mean().reset_index()
    fig_avg_load = px.bar(avg_load, x="Truck No", y="Volume", text="Volume", color="Truck No",
                          color_discrete_sequence=color_palette, title="Avg Load per Trip")
    fig_avg_load.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(styled_chart(fig_avg_load), use_container_width=True)

    # =========================
    # 5. Distance Analysis
    # =========================
    st.subheader("📍 Distance Analysis")
    col_dist_plant, col_dist_area = st.columns(2)
    with col_dist_plant:
        avg_dist_plant = df_filtered.groupby("Plant Name")["Distance"].mean().reset_index()
        fig_dist_plant = px.bar(avg_dist_plant, x="Plant Name", y="Distance", text="Distance",
                                title="Avg Distance per Plant")
        fig_dist_plant.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(styled_chart(fig_dist_plant), use_container_width=True)
    with col_dist_area:
        avg_dist_area = df_filtered.groupby("Area")["Distance"].mean().reset_index()
        fig_dist_area = px.bar(avg_dist_area, x="Area", y="Distance", text="Distance",
                               title="Avg Distance per Area")
        fig_dist_area.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(styled_chart(fig_dist_area), use_container_width=True)

    # =========================
    # 6. Sales & Customer Performance (FULL WIDTH)
    # =========================
    st.markdown("<hr><h2>👤 Sales & Customer Performance</h2>", unsafe_allow_html=True)
    sales_perf = df_filtered.groupby("Sales Man")["Volume"].sum().reset_index().sort_values("Volume", ascending=False)
    fig_sales = px.bar(sales_perf, x="Sales Man", y="Volume", text="Volume", color="Sales Man",
                       color_discrete_sequence=color_palette, title="Volume per Sales")
    fig_sales.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(styled_chart(fig_sales, height=500), use_container_width=True)

    cust_perf = df_filtered.groupby("End Customer Name")["Volume"].sum().reset_index().sort_values("Volume", ascending=False)
    if not cust_perf.empty:
        fig_cust = px.bar(cust_perf, x="End Customer Name", y="Volume", text="Volume", color="End Customer Name",
                          color_discrete_sequence=color_palette, title="Volume per End Customer Name")
        fig_cust.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(styled_chart(fig_cust, height=500), use_container_width=True)
    else:
        st.info("No data available for End Customer Name")

else:
    st.info("📤 Silakan upload file Excel terlebih dahulu untuk menampilkan dashboard.")
