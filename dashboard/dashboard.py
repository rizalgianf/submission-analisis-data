import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

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
    avg_pm10 = data_filtered["PM10"].mean()
    avg_co = data_filtered["CO"].mean()
    
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
    st.write(f"**PM10 Rata-rata**: {avg_pm10:.2f} µg/m³")
    st.write(f"**CO Rata-rata**: {avg_co:.2f} ppm")
    
    # Grafik PM2.5, PM10, dan CO sepanjang bulan
    if bulan == "Keseluruhan Bulan":
        daily_avg = data_filtered.groupby(["year", "month", "day"])[['PM2.5', 'PM10', 'CO']].mean().reset_index()
    else:
        daily_avg = data_filtered.groupby("day")[['PM2.5', 'PM10', 'CO']].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(daily_avg.index, daily_avg["PM2.5"], label="PM2.5", color="red")
    ax.plot(daily_avg.index, daily_avg["PM10"], label="PM10", color="blue")
    ax.plot(daily_avg.index, daily_avg["CO"], label="CO", color="green")
    ax.set_xlabel("Hari")
    ax.set_ylabel("Konsentrasi µg/m³ / ppm")
    ax.set_title(f"Perubahan PM2.5, PM10, dan CO di {location} - {bulan}/{tahun}")
    ax.legend()
    st.pyplot(fig)
    
    # Menampilkan tabel rata-rata harian
    st.subheader("📋 Rata-rata Kualitas Udara per Hari")
    st.dataframe(daily_avg)
    
    # Analisis pengaruh suhu dan kelembaban terhadap PM2.5
    st.subheader("📊 Analisis Pengaruh Suhu dan Kelembaban terhadap PM2.5")
    
    # Scatter plot PM2.5 vs TEMP
    fig, ax = plt.subplots()
    ax.scatter(data_filtered["TEMP"], data_filtered["PM2.5"], alpha=0.5)
    ax.set_xlabel("Suhu (°C)")
    ax.set_ylabel("PM2.5 (µg/m³)")
    ax.set_title("Pengaruh Suhu terhadap PM2.5")
    st.pyplot(fig)
    
    # Scatter plot PM2.5 vs DEWP
    fig, ax = plt.subplots()
    ax.scatter(data_filtered["DEWP"], data_filtered["PM2.5"], alpha=0.5)
    ax.set_xlabel("Kelembaban (°C)")
    ax.set_ylabel("PM2.5 (µg/m³)")
    ax.set_title("Pengaruh Kelembaban terhadap PM2.5")
    st.pyplot(fig)
    
    # Korelasi antara PM2.5 dengan TEMP dan DEWP
    correlation_temp = data_filtered["PM2.5"].corr(data_filtered["TEMP"])
    correlation_dewp = data_filtered["PM2.5"].corr(data_filtered["DEWP"])
    
    st.write(f"Korelasi antara PM2.5 dan Suhu: {correlation_temp:.2f}")
    st.write(f"Korelasi antara PM2.5 dan Kelembaban: {correlation_dewp:.2f}")
    
else:
    st.write("⚠️ Data PM2.5 tidak tersedia untuk lokasi ini.")