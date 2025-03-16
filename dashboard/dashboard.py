import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import geopandas as gpd
from shapely.geometry import Point
import folium
from folium.plugins import HeatMap

# Path folder dataset (sesuaikan jika berbeda)
data_folder = os.path.join(os.path.dirname(__file__), 'main_data', 'PRSA_Data_20130301-20170228')

# Fungsi untuk memuat semua dataset
def load_data():
    if not os.path.exists(data_folder):
        st.error(f"Folder data tidak ditemukan: {data_folder}")
        return {}
    
    data_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
    all_data = {}
    
    for file in data_files:
        location = file.replace("PRSA_Data_", "").split("_")[0]  # Ambil nama lokasi
        file_path = os.path.join(data_folder, file)
        df = pd.read_csv(file_path)
        
        # Bersihkan nama kolom dari spasi tersembunyi
        df.columns = df.columns.str.strip()
        all_data[location] = df
    
    return all_data

# Load semua data
all_data = load_data()

# Sidebar untuk navigasi
st.sidebar.title("📍 Pilih Lokasi dan Periode")
locations = list(all_data.keys())
locations.insert(0, "Keseluruhan Lokasi")
location = st.sidebar.selectbox("Pilih Lokasi", locations)

if location == "Keseluruhan Lokasi":
    data = pd.concat(all_data.values())
else:
    data = all_data[location]

years = data["year"].unique().tolist()
years.insert(0, "Keseluruhan Tahun")
tahun = st.sidebar.selectbox("Pilih Tahun", years)

if tahun == "Keseluruhan Tahun":
    data_filtered = data
else:
    data_filtered = data[data["year"] == tahun]

bulan = st.sidebar.selectbox("Pilih Bulan", ["Keseluruhan Bulan"] + data["month"].unique().tolist())

if bulan != "Keseluruhan Bulan":
    data_filtered = data_filtered[data_filtered["month"] == bulan]

# Menampilkan informasi dasar
st.title(f"🌍 Dashboard Kualitas Udara - {location}")
st.write(f"Menampilkan data untuk {bulan}-{tahun}")

# Pastikan kolom PM2.5 tersedia
if "PM2.5" in data_filtered.columns:
    avg_pm25 = data_filtered["PM2.5"].mean()
    
    # Status kualitas udara berdasarkan PM2.5
    def categorize_air_quality(pm25):
        if pm25 <= 12:
            return "Baik ✅"
        elif pm25 <= 35:
            return "Sedang 🟡"
        elif pm25 <= 55:
            return "Tidak Sehat ⚠️"
        else:
            return "Buruk ❌"

    air_quality = categorize_air_quality(avg_pm25)
    
    st.markdown(f"### 🌬️ Status Udara: **{air_quality}**")
    st.write(f"**PM2.5 Rata-rata**: {avg_pm25:.2f} µg/m³")
    
    # Pastikan kolom 'date' sudah dalam format datetime
    data_filtered['date'] = pd.to_datetime(data_filtered[['year', 'month', 'day']])

    # Mengisi nilai NaN dengan median pada kolom PM2.5
    data_filtered['PM2.5'] = data_filtered['PM2.5'].fillna(data_filtered['PM2.5'].median())

    # Grafik PM2.5 sepanjang waktu
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(data_filtered['date'], data_filtered["PM2.5"], label="PM2.5", color="blue")
    ax.set_xlabel("Tanggal", fontsize=12)
    ax.set_ylabel("Konsentrasi PM2.5 (µg/m³)", fontsize=12)
    ax.set_title(f"Tren Kualitas Udara (PM2.5) di {location} - {bulan}/{tahun}", fontsize=14)
    ax.set_ylim(0, 1000)  # Set rentang sumbu y dari 0 hingga 1000
    ax.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Tambahkan kolom untuk menentukan apakah hari kerja atau akhir pekan
    data_filtered['day_of_week'] = data_filtered['date'].dt.dayofweek  # 0 = Senin, 6 = Minggu
    data_filtered['is_weekend'] = data_filtered['day_of_week'].apply(lambda x: 'Akhir Pekan' if x >= 5 else 'Hari Kerja')

    # Hitung rata-rata PM2.5 untuk hari kerja dan akhir pekan
    avg_pm25 = data_filtered.groupby('is_weekend')['PM2.5'].mean().reset_index()

    # Menampilkan informasi rata-rata PM2.5
    st.subheader("📊 Perbandingan Rata-rata PM2.5 antara Hari Kerja dan Akhir Pekan")
    st.write(avg_pm25)

    # Visualisasi perbedaan rata-rata PM2.5
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(avg_pm25['is_weekend'], avg_pm25['PM2.5'], color=['blue', 'orange'])
    ax.set_title('Perbedaan Rata-rata PM2.5 antara Hari Kerja dan Akhir Pekan', fontsize=14)
    ax.set_xlabel('Kategori Hari', fontsize=12)
    ax.set_ylabel('Rata-rata PM2.5 (µg/m³)', fontsize=12)
    st.pyplot(fig)

    # Menambahkan analisis geospasial di bagian paling bawah
    st.subheader("🌍 Visualisasi Geospasial Konsentrasi PM2.5")
    
    # Menambahkan informasi geospasial (latitude dan longitude)
    station_coords = {
        'Aotizhongxin': (39.982, 116.306),
        'Changping': (40.218, 116.231),
        'Dingling': (40.292, 116.220),
        'Dongsi': (39.929, 116.417),
        'Guanyuan': (39.929, 116.365),
        'Gucheng': (39.911, 116.146),
        'Huairou': (40.375, 116.628),
        'Nongzhanguan': (39.933, 116.467),
        'Shunyi': (40.127, 116.655),
        'Tiantan': (39.886, 116.407),
        'Wanshouxigong': (39.878, 116.352),
        'Wanliu': (39.999, 116.305)
    }
    data_filtered['latitude'] = data_filtered['station'].apply(lambda x: station_coords[x][0])
    data_filtered['longitude'] = data_filtered['station'].apply(lambda x: station_coords[x][1])

    # Mengambil sampel data untuk mengurangi beban pemrosesan
    sample_data = data_filtered.sample(n=500, random_state=42)

    # Membuat peta dasar menggunakan folium
    m = folium.Map(location=[39.9042, 116.4074], zoom_start=9)

    # Menambahkan marker untuk setiap stasiun
    for idx, row in sample_data.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"Stasiun: {row['station']}<br>PM2.5: {row['PM2.5']}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

    # Menambahkan HeatMap untuk visualisasi konsentrasi PM2.5
    heat_data = [[row['latitude'], row['longitude'], row['PM2.5']] for index, row in sample_data.iterrows() if not pd.isna(row['PM2.5'])]
    HeatMap(heat_data, radius=65).add_to(m)

    # Menampilkan peta di Streamlit
    st.markdown("### Peta Geospasial Konsentrasi PM2.5 (Sampel Data)")
    st.components.v1.html(m._repr_html_(), height=600)

else:
    st.write("⚠️ Data PM2.5 tidak tersedia untuk lokasi ini.")