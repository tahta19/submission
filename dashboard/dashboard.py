# Import library
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style seaborn
sns.set_style("whitegrid")

# Judul dashboard
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")
st.title("Bike Sharing Dashboard - Analisis Permintaan Sepeda")

# Load data
data = pd.read_csv("dashboard/main_data.csv")

# Sidebar filter
st.sidebar.header("Filter Data")
year_filter = st.sidebar.multiselect("Tahun", options=data['year_label'].unique(), default=data['year_label'].unique())
month_filter = st.sidebar.multiselect("Bulan", options=data['month_name'].unique(), default=data['month_name'].unique())
workingday_filter = st.sidebar.selectbox("Hari Kerja?", options=[0,1], format_func=lambda x: "Weekend" if x==0 else "Weekday")
weather_filter = st.sidebar.multiselect("Cuaca", options=data['weather_label'].unique(), default=data['weather_label'].unique())

# Apply filter
filtered_data = data[
    (data['year_label'].isin(year_filter)) &
    (data['month_name'].isin(month_filter)) &
    (data['workingday'] == workingday_filter) &
    (data['weather_label'].isin(weather_filter))
]

# KPI cards
st.subheader("Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Penyewaan", int(filtered_data['cnt'].sum()))
col2.metric("Registered Users", int(filtered_data['registered'].sum()))
col3.metric("Casual Users", int(filtered_data['casual'].sum()))

# Visualization 1: Time Segment vs Count
st.subheader("Jumlah Penyewaan per Time Segment")
time_segment_avg = filtered_data.groupby('time_segment')['cnt'].mean().reset_index()
fig1, ax1 = plt.subplots()
sns.barplot(x='time_segment', y='cnt', data=time_segment_avg, ax=ax1)
ax1.set_ylabel("Rata-rata Penyewaan")
ax1.set_xlabel("Time Segment")
st.pyplot(fig1)

# Visualization 2: Season & Weather vs Count
st.subheader("Jumlah Penyewaan per Musim & Kondisi Cuaca")
season_weather_avg = filtered_data.groupby(['season_label','weather_label'])['cnt'].mean().reset_index()
fig2, ax2 = plt.subplots(figsize=(10,5))
sns.barplot(x='season_label', y='cnt', hue='weather_label', data=season_weather_avg, ax=ax2)
ax2.set_ylabel("Rata-rata Penyewaan")
ax2.set_xlabel("Musim")
st.pyplot(fig2)

# Visualization 3: Casual vs Registered per Jam
st.subheader("Perbandingan Casual vs Registered per Jam")
hourly_avg = filtered_data.groupby('hr')[['casual','registered']].mean().reset_index()
fig3, ax3 = plt.subplots(figsize=(12,5))
sns.lineplot(x='hr', y='casual', data=hourly_avg, label='Casual', marker='o', ax=ax3)
sns.lineplot(x='hr', y='registered', data=hourly_avg, label='Registered', marker='o', ax=ax3)
ax3.set_xlabel("Jam")
ax3.set_ylabel("Rata-rata Penyewaan")
ax3.set_xticks(range(0,24))
st.pyplot(fig3)

st.markdown("""
### Catatan:
- Gunakan filter di sidebar untuk menyesuaikan data berdasarkan tahun, bulan, hari kerja, dan cuaca.
- Semua grafik menampilkan **rata-rata penyewaan** berdasarkan data yang telah difilter.
""")