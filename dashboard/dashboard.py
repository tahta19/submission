import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime

# ============================
# Load Data (Path Aman)
# ============================
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "main_data.csv")

@st.cache_data
def load_data():
    """Load and parse bike sharing data with proper date handling"""
    return pd.read_csv(DATA_PATH, parse_dates=['dteday'])

df = load_data()

# ============================
# Page Config
# ============================
st.set_page_config(
    page_title="Bike Sharing Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("🚴 Bike Sharing Analysis Dashboard - Pro Version")
st.markdown("**Data Source:** Capital Bike Share System (2011-2012, Washington D.C.)")

# ============================
# Sidebar Filter
# ============================
st.sidebar.header("📊 Filter Data")

# Tahun
tahun_options = sorted(df['year_label'].unique().tolist())
selected_years = st.sidebar.multiselect(
    "📅 Tahun", 
    tahun_options, 
    default=tahun_options,
    help="Pilih satu atau lebih tahun untuk analisis"
)

# Bulan
bulan_options = df['month_name'].unique().tolist()
selected_months = st.sidebar.multiselect(
    "📆 Bulan", 
    bulan_options, 
    default=bulan_options,
    help="Pilih satu atau lebih bulan"
)

# Hari Kerja / Weekend
hari_opsi = ['Weekday', 'Weekend']
selected_hari = st.sidebar.selectbox(
    "📋 Hari Kerja?", 
    hari_opsi,
    help="Filter berdasarkan hari kerja atau weekend"
)

# Cuaca
cuaca_options = df['weather_label'].unique().tolist()
selected_cuaca = st.sidebar.multiselect(
    "🌤️ Cuaca", 
    cuaca_options, 
    default=cuaca_options,
    help="Pilih kondisi cuaca untuk dianalisis"
)

# Filter Tanggal Range (Baru)
st.sidebar.markdown("---")
st.sidebar.subheader("📅 Filter Tanggal Range")
min_date = df['dteday'].min()
max_date = df['dteday'].max()

col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "Mulai dari", 
        value=min_date,
        min_value=min_date,
        max_value=max_date
    )
with col2:
    end_date = st.date_input(
        "Sampai", 
        value=max_date,
        min_value=min_date,
        max_value=max_date
    )

# ============================
# Apply Filter
# ============================
filtered_df = df[
    (df['year_label'].isin(selected_years)) &
    (df['month_name'].isin(selected_months)) &
    (df['weekday_name'].apply(lambda x: 'Weekend' if x in ['Saturday', 'Sunday'] else 'Weekday') == selected_hari) &
    (df['weather_label'].isin(selected_cuaca)) &
    (df['dteday'] >= pd.to_datetime(start_date)) &
    (df['dteday'] <= pd.to_datetime(end_date))
]

# Display filter info
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📊 Data Rows", f"{len(filtered_df):,}")
with col2:
    st.metric("📈 Avg Daily Rentals", f"{filtered_df['cnt'].mean():.0f}")
with col3:
    st.metric("📅 Date Range", f"{(filtered_df['dteday'].max() - filtered_df['dteday'].min()).days} days")

st.divider()

# ============================
# KPI Cards
# ============================
st.subheader("🎯 Key Performance Indicators")
kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

with kpi_col1:
    st.metric(
        "Total Penyewaan",
        f"{filtered_df['cnt'].sum():,.0f}",
        delta=f"{(filtered_df['cnt'].sum() / df['cnt'].sum() * 100):.1f}% dari total"
    )

with kpi_col2:
    registered_total = filtered_df['registered'].sum()
    st.metric(
        "Registered Users",
        f"{registered_total:,.0f}",
        delta=f"{(registered_total / filtered_df['cnt'].sum() * 100):.1f}% dari total"
    )

with kpi_col3:
    casual_total = filtered_df['casual'].sum()
    st.metric(
        "Casual Users",
        f"{casual_total:,.0f}",
        delta=f"{(casual_total / filtered_df['cnt'].sum() * 100):.1f}% dari total"
    )

st.divider()

# ============================
# Time Segment Visualization
# ============================
st.subheader("⏰ Rata-rata Penyewaan Sepeda per Time Segment")
time_segment_df = filtered_df.groupby('time_segment')['cnt'].mean().reset_index().sort_values('cnt', ascending=False)
time_segment_order = ['Morning', 'Afternoon', 'Evening', 'Night']
time_segment_df['time_segment'] = pd.Categorical(time_segment_df['time_segment'], categories=time_segment_order, ordered=True)
time_segment_df = time_segment_df.sort_values('time_segment')

fig_ts = px.bar(
    time_segment_df, 
    x='time_segment', 
    y='cnt',
    color='time_segment', 
    text='cnt',
    color_discrete_sequence=px.colors.qualitative.Pastel,
    labels={'cnt': 'Rata-rata Penyewaan', 'time_segment': 'Time Segment'},
    title="Pola Penyewaan Sepeda Berdasarkan Waktu"
)
fig_ts.update_traces(
    texttemplate='%{text:.0f}', 
    textposition='outside',
    hovertemplate='<b>%{x}</b><br>Rata-rata: %{y:.0f} penyewaan<extra></extra>'
)
fig_ts.update_layout(
    showlegend=False,
    xaxis_title="Time Segment",
    yaxis_title="Rata-rata Penyewaan",
    height=400
)
st.plotly_chart(fig_ts, use_container_width=True)

# ============================
# Season & Weather Visualization
# ============================
st.subheader("🌍 Penyewaan per Musim & Kondisi Cuaca")
season_weather_df = filtered_df.groupby(['season_label', 'weather_label'])['cnt'].mean().reset_index()

fig_sw = px.bar(
    season_weather_df,
    x='season_label',
    y='cnt',
    color='weather_label',
    barmode='group',
    labels={'cnt': 'Rata-rata Penyewaan', 'season_label': 'Musim', 'weather_label': 'Kondisi Cuaca'},
    title="Pengaruh Musim dan Cuaca terhadap Penyewaan",
    color_discrete_sequence=px.colors.qualitative.Set2
)
fig_sw.update_layout(
    height=400,
    hovermode='x unified'
)
st.plotly_chart(fig_sw, use_container_width=True)

# ============================
# Casual vs Registered
# ============================
st.subheader("👥 Perbandingan Perilaku Casual vs Registered User")
hourly_df = filtered_df.groupby('hr')[['casual', 'registered']].mean().reset_index()

fig_cr = go.Figure()
fig_cr.add_trace(go.Scatter(
    x=hourly_df['hr'], 
    y=hourly_df['casual'],
    mode='lines+markers', 
    name='Casual User',
    line=dict(color='royalblue', width=3),
    marker=dict(size=8),
    hovertemplate='<b>Jam %{x}:00</b><br>Casual: %{y:.0f}<extra></extra>'
))
fig_cr.add_trace(go.Scatter(
    x=hourly_df['hr'], 
    y=hourly_df['registered'],
    mode='lines+markers', 
    name='Registered User',
    line=dict(color='darkorange', width=3),
    marker=dict(size=8),
    hovertemplate='<b>Jam %{x}:00</b><br>Registered: %{y:.0f}<extra></extra>'
))
fig_cr.update_layout(
    title="Pola Penggunaan Sepeda Casual vs Registered per Jam",
    xaxis_title="Jam (24-hour format)",
    yaxis_title="Rata-rata Penyewaan",
    height=400,
    hovermode='x unified',
    template='plotly_white'
)
fig_cr.update_xaxes(tickmode='linear', tick0=0, dtick=1)
st.plotly_chart(fig_cr, use_container_width=True)

# ============================
# RFM Analysis + Clustering
# ============================
st.subheader("💰 RFM Analysis: Segmentasi Pelanggan")

rfm_df = filtered_df.groupby('dteday').agg({
    'cnt': 'sum',
    'casual': 'sum',
    'registered': 'sum'
}).reset_index()

# Calculate RFM metrics
max_date = rfm_df['dteday'].max()
rfm_df['Recency'] = (max_date - rfm_df['dteday']).dt.days
rfm_df['Frequency'] = rfm_df['cnt']
rfm_df['Monetary'] = rfm_df['cnt']

# Segmentasi menggunakan Monetary value
rfm_df['Segment'] = pd.qcut(
    rfm_df['Monetary'], 
    q=4, 
    labels=['Low', 'Medium', 'High', 'Very High'],
    duplicates='drop'
)

# Color mapping untuk segment
color_map = {
    'Low': '#FF6B6B',
    'Medium': '#FFA500',
    'High': '#4ECDC4',
    'Very High': '#2ECC71'
}

fig_rfm = px.bar(
    rfm_df, 
    x='dteday', 
    y='cnt', 
    color='Segment',
    labels={'cnt': 'Total Penyewaan', 'dteday': 'Tanggal'},
    title="Segmentasi Pelanggan Berdasarkan Penyewaan Harian",
    color_discrete_map=color_map
)
fig_rfm.update_traces(
    hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Total Penyewaan: %{y}<br>Segment: %{marker.color}<extra></extra>'
)
fig_rfm.update_layout(
    height=400,
    xaxis_title="Tanggal",
    yaxis_title="Total Penyewaan"
)
st.plotly_chart(fig_rfm, use_container_width=True)

# RFM Summary Stats
rfm_col1, rfm_col2, rfm_col3 = st.columns(3)
with rfm_col1:
    st.metric("Avg Recency (days)", f"{rfm_df['Recency'].mean():.1f}")
with rfm_col2:
    st.metric("Avg Frequency", f"{rfm_df['Frequency'].mean():.0f}")
with rfm_col3:
    st.metric("Avg Monetary", f"{rfm_df['Monetary'].mean():.0f}")

st.divider()

# ============================
# Date Detail Analysis
# ============================
st.subheader("📅 Analisis Detail Tanggal")

col_date1, col_date2 = st.columns(2)

with col_date1:
    st.markdown("**Statistik Tanggal yang Dipilih:**")
    date_stats = f"""
    - **Total Hari Data:** {len(rfm_df)} hari
    - **Range Tanggal:** {rfm_df['dteday'].min().strftime('%d %B %Y')} hingga {rfm_df['dteday'].max().strftime('%d %B %Y')}
    - **Total Penyewaan:** {rfm_df['cnt'].sum():,.0f}
    - **Penyewaan Tertinggi:** {rfm_df['cnt'].max():,.0f} ({rfm_df.loc[rfm_df['cnt'].idxmax(), 'dteday'].strftime('%d %B %Y')})
    - **Penyewaan Terendah:** {rfm_df['cnt'].min():,.0f} ({rfm_df.loc[rfm_df['cnt'].idxmin(), 'dteday'].strftime('%d %B %Y')})
    """
    st.markdown(date_stats)

with col_date2:
    st.markdown("**Breakdown Segment:**")
    segment_counts = rfm_df['Segment'].value_counts().sort_index()
    for segment in ['Low', 'Medium', 'High', 'Very High']:
        if segment in segment_counts.index:
            count = segment_counts[segment]
            percentage = (count / len(rfm_df) * 100)
            st.write(f"• **{segment}:** {count} hari ({percentage:.1f}%)")

st.divider()

# ============================
# Date Picker untuk Single Day Analysis
# ============================
st.subheader("🔍 Single Date Analysis")

min_date_range = filtered_df['dteday'].min()
max_date_range = filtered_df['dteday'].max()

selected_date = st.date_input(
    "Pilih Tanggal untuk Analisis Detail:",
    value=max_date_range,
    min_value=min_date_range,
    max_value=max_date_range,
    help="Pilih tanggal tertentu untuk melihat detail penyewaan per jam"
)

# Get data for selected date
selected_date_data = filtered_df[filtered_df['dteday'].dt.date == selected_date]

if len(selected_date_data) > 0:
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        day_name = pd.to_datetime(selected_date).strftime('%A')
        is_weekend = "✅ Weekend" if pd.to_datetime(selected_date).weekday() in [5, 6] else "✅ Weekday"
        st.metric("Jenis Hari", is_weekend)
    
    with col_info2:
        st.metric("Total Penyewaan", f"{selected_date_data['cnt'].sum():,.0f}")
    
    with col_info3:
        st.metric("Cuaca", selected_date_data['weather_label'].iloc[0])
    
    # Hourly breakdown for selected date
    st.markdown(f"**Breakdown Penyewaan per Jam - {selected_date.strftime('%d %B %Y')}:**")
    hourly_selected = selected_date_data.groupby('hr')[['casual', 'registered', 'cnt']].sum().reset_index()
    
    fig_selected = go.Figure()
    fig_selected.add_trace(go.Bar(
        x=hourly_selected['hr'],
        y=hourly_selected['casual'],
        name='Casual',
        marker_color='lightblue'
    ))
    fig_selected.add_trace(go.Bar(
        x=hourly_selected['hr'],
        y=hourly_selected['registered'],
        name='Registered',
        marker_color='darkorange'
    ))
    
    fig_selected.update_layout(
        barmode='stack',
        title=f"Penyewaan per Jam - {selected_date.strftime('%d %B %Y')}",
        xaxis_title="Jam",
        yaxis_title="Jumlah Penyewaan",
        height=400,
        hovermode='x unified'
    )
    fig_selected.update_xaxes(tickmode='linear', tick0=0, dtick=1)
    st.plotly_chart(fig_selected, use_container_width=True)
    
    # Display table
    st.dataframe(
        hourly_selected.rename(columns={
            'hr': 'Jam',
            'casual': 'Casual',
            'registered': 'Registered',
            'cnt': 'Total'
        }),
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("⚠️ Tidak ada data untuk tanggal yang dipilih")

st.divider()

# ============================
# Footer
# ============================
st.markdown("""
---
### 📌 Informasi Dashboard
- **Data Source:** Bike Sharing Dataset (2011-2012, Capital Bike Share System, Washington D.C.)
- **Last Updated:** {} 
- **Dashboard Version:** 2.0 - Pro Version
- **Created with:** Streamlit + Plotly

**Fitur:**
- ✅ Filter Data Interaktif (Tahun, Bulan, Hari, Cuaca, Tanggal Range)
- ✅ Analisis Time Segment
- ✅ Perbandingan Casual vs Registered User
- ✅ RFM Segmentation Analysis
- ✅ Single Date Detail Analysis
- ✅ Responsive Design
""".format(datetime.now().strftime('%d %B %Y, %H:%M:%S')))