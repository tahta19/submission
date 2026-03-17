# Bike Sharing Dashboard

## Deskripsi
Dashboard ini menampilkan analisis permintaan sepeda dari **Bike Sharing Dataset** (2011-2012, Capital Bike Share System, Washington D.C., USA). Dashboard dibuat menggunakan **Streamlit** dan menampilkan:
- Rata-rata penyewaan sepeda per **Time Segment** (Morning, Afternoon, Evening, Night) dan per **jenis hari** (Weekday/Weekend)
- Rata-rata penyewaan per **Musim** dan **Kondisi Cuaca**
- Perbandingan **Casual vs Registered Users** per jam

Dashboard memungkinkan pengguna untuk **memfilter data** berdasarkan tahun, bulan, hari kerja, dan kondisi cuaca.
Link Dashboard : https://dashboard-bike-sharing-tahta19.streamlit.app/

## Struktur Folder
submission/

├── dashboard/

│ ├── main_data.csv

│ └── dashboard.py

├── data/

│ ├── hour.csv

│ └── day.csv

├── notebook.ipynb

├── README.md

├── requirements.txt

└── url.txt (opsional jika deploy online)


## Cara Menjalankan Dashboard
1. Pastikan Python 3.8+ terinstal
2. Install library yang dibutuhkan:
```bash
- pip install -r requirements.txt
- Jalankan dashboard:
- streamlit run dashboard/dashboard.py
- Dashboard akan terbuka di browser default pada localhost:8501.

Fitur Interaktif
- Sidebar filter untuk tahun, bulan, hari kerja, dan cuaca
- KPI cards menampilkan total penyewaan, casual, dan registered users
- Grafik interaktif menggunakan Seaborn dan Matplotlib
- Analisis lanjutan menunjukkan pola perilaku pengguna berdasarkan waktu, hari, dan kondisi cuaca
