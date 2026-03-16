import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ============================
# Load Data (Path Aman)
# ============================
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "main_data.csv")

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH, parse_dates=['dteday'])

df = load_data()

# ============================
# Page Config
# ============================
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")
st.title("🚴 Bike Sharing Analysis Dashboard - Pro Version")

# ============================
# Sidebar Filter
# ============================
st.sidebar.header("Filter Data")

# Tahun
tahun_options = df['year_label'].unique().tolist()
selected_years = st.sidebar.multiselect("Tahun", tahun_options, default=tahun_options)

# Bulan
bulan_options = df['month_name'].unique().tolist()
selected_months = st.sidebar.multiselect("Bulan", bulan_options, default=bulan_options)

# Hari Kerja / Weekend
hari_opsi = ['Weekday','Weekend']
selected_hari = st.sidebar.selectbox("Hari Kerja?", hari_opsi)

# Cuaca
cuaca_options = df['weather_label'].unique().tolist()
selected_cuaca = st.sidebar.multiselect("Cuaca", cuaca_options, default=cuaca_options)

# Apply filter
filtered_df = df[
    (df['year_label'].isin(selected_years)) &
    (df['month_name'].isin(selected_months)) &
    (df['weekday_name'].apply(lambda x: 'Weekend' if x in ['Saturday','Sunday'] else 'Weekday') == selected_hari) &
    (df['weather_label'].isin(selected_cuaca))
]

st.markdown(f"**Jumlah Data Setelah Filter:** {len(filtered_df)} rows")

# ============================
# Time Segment Visualization
# ============================
st.subheader("Rata-rata Penyewaan Sepeda per Time Segment")
time_segment_df = filtered_df.groupby('time_segment')['cnt'].mean().reset_index()
fig_ts = px.bar(time_segment_df, x='time_segment', y='cnt',
                color='time_segment', text='cnt',
                color_discrete_sequence=px.colors.qualitative.Pastel,
                labels={'cnt':'Rata-rata Penyewaan', 'time_segment':'Time Segment'})
fig_ts.update_traces(texttemplate='%{text:.1f}', textposition='outside',
                     hovertemplate='Segment: %{x}<br>Rata-rata: %{y}')
st.plotly_chart(fig_ts, use_container_width=True)

# ============================
# Casual vs Registered
# ============================
st.subheader("Perbandingan Perilaku Casual vs Registered")
hourly_df = filtered_df.groupby('hr')[['casual','registered']].mean().reset_index()
fig_cr = go.Figure()
fig_cr.add_trace(go.Scatter(x=hourly_df['hr'], y=hourly_df['casual'],
                            mode='lines+markers', name='Casual',
                            line=dict(color='royalblue')))
fig_cr.add_trace(go.Scatter(x=hourly_df['hr'], y=hourly_df['registered'],
                            mode='lines+markers', name='Registered',
                            line=dict(color='darkorange')))
fig_cr.update_layout(title="Casual vs Registered per Jam", xaxis_title="Jam", yaxis_title="Rata-rata Penyewaan")
st.plotly_chart(fig_cr, use_container_width=True)

# ============================
# RFM Analysis + Clustering
# ============================
st.subheader("RFM Analysis: Segmentasi Pelanggan")
rfm_df = filtered_df.groupby('dteday').agg({
    'cnt':'sum',
    'casual':'sum',
    'registered':'sum'
}).reset_index()
rfm_df['Recency'] = (rfm_df['dteday'].max() - rfm_df['dteday']).dt.days
rfm_df['Frequency'] = rfm_df['cnt']
rfm_df['Monetary'] = rfm_df['cnt']

# Clustering manual (qcut)
rfm_df['Segment'] = pd.qcut(rfm_df['Monetary'], q=4, labels=['Low','Medium','High','Very High'])

fig_rfm = px.bar(rfm_df, x='dteday', y='cnt', color='Segment', 
                 labels={'cnt':'Total Penyewaan', 'dteday':'Tanggal'}, 
                 color_discrete_sequence=px.colors.sequential.Viridis)
fig_rfm.update_traces(hovertemplate='Tanggal: %{x}<br>Total: %{y}<br>Segment: %{marker.color}')
st.plotly_chart(fig_rfm, use_container_width=True)

# ============================
# Filter Tanggal (Kalender)
# ============================
st.subheader("Filter Tanggal (Weekend Highlighted)")
min_date = filtered_df['dteday'].min()
max_date = filtered_df['dteday'].max()
selected_date = st.date_input("Pilih Tanggal:", min_value=min_date, max_value=max_date)

if pd.to_datetime(selected_date).weekday() in [5,6]:
    st.info("Tanggal ini adalah weekend")
else:
    st.success("Tanggal ini adalah weekday")