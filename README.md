# Data Lifecycle Smart Farming 🌾

Dashboard monitoring dan analisis data sensor pertanian berbasis IoT yang dibangun menggunakan Python dan Streamlit. Dashboard ini dirancang untuk memvisualisasikan data dari sensor IoT di lahan pertanian secara interaktif, mulai dari kondisi tanah, cuaca, hingga hasil panen.

📁 Struktur Folder

Smart-Farming-Dashboard/

├── data/raw/smart_farming_sensor_data.csv                  
├── Data_Lifecycle_Smart_Farming.ipynb               
├── dashboard/streamlit_app.py    
├── README.md               
└── outputs/  

            ├── cleaned_data.csv
            ├── Laporan Analisis Report.pdf
            └── dashboard_screenshot.png

      
📊 Fitur Dashboard
Dashboard terdiri dari 7 section utama:
1. KPI Metrics: 5 kartu ringkasan> total farm, rata-rata yield, NDVI, suhu, dan kelembaban tanah
2. Alert System: Sistem peringatan otomatis jika sensor mendeteksi kondisi di luar batas aman
3. Gauge Meter: Speedometer 4 sensor utama dengan indikator zona aman/bahaya
4. Grafik Yield: Bar chart produktivitas per jenis tanaman dan per metode irigasi
5. Time Series: Tren perubahan nilai sensor dari bulan ke bulan
6. Heatmap Korelasi: Matriks hubungan antar variabel sensor dan hasil panen
7. Data Mentah: Tabel lengkap seluruh data yang dapat di-scroll.

🗃️ Tentang Dataset

Dataset berisi data dari 255 farm di 5 wilayah berbeda dengan 22 variabel yang dikumpulkan dari sensor IoT.

🛠️ Teknologi yang Digunakan
1. streamlit: Framework web dashboard interaktif
2. plotly: Grafik interaktif (bar, scatter, gauge, heatmap, time series)
3. pandas: Manipulasi dan analisis data
4. numpy: Komputasi numerik
5. seaborn & matplotlib: Grafik statistik tambahan
