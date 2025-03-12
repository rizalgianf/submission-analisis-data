README - Dashboard Kualitas Udara

Deskripsi

Dashboard ini dibuat pakai Streamlit buat nampilin analisis kualitas udara dari dataset PRSA Data. Pengguna bisa pilih lokasi, tahun, dan bulan buat lihat tren kualitas udara lewat grafik dan tabel interaktif.

Fitur Utama

Pilih Lokasi → Bisa milih kota/daerah yang ada di dataset.

Filter Waktu → Pilih tahun dan bulan buat lihat data sesuai periode.

Analisis Kualitas Udara → Nampilin rata-rata PM2.5, PM10, dan CO.

Status Udara → Ada indikator Baik, Sedang, Tidak Sehat, atau Buruk.

Grafik Tren Harian → Lihat perubahan PM2.5, PM10, dan CO dalam satu bulan.

Tabel Rata-rata Harian → Buat yang butuh detail angka per hari.

Persiapan

Python 3.x

Streamlit

Pandas

Matplotlib

Cara Instal

Download atau clone repo ini

Install paket yang dibutuhkan

pip install streamlit pandas matplotlib

Pastikan dataset ada di folder yang sesuai.

Cara Jalanin

Masuk ke folder proyek via terminal/cmd

cd dashboard

Jalankan aplikasi Streamlit

streamlit run dashboard.py

Akses dashboard di browser (biasanya otomatis ke http://localhost:8501).

Cara Pakai

Pilih lokasi yang mau dianalisis dari sidebar.

Pilih tahun dan bulan buat lihat data spesifik.

Lihat ringkasan kualitas udara termasuk PM2.5, PM10, dan CO.

Cek grafik tren harian buat lihat perubahan polusi tiap hari.

Gunakan tabel rata-rata harian buat detail angka harian.

Catatan

Kalau dataset berubah format, pastikan kolom-kolomnya bersih dari spasi tersembunyi.

Kalau ada error soal PM2.5, cek apakah dataset beneran punya kolom itu.