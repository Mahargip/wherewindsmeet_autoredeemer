# 🎮 Where Winds Meet - Auto Code Redeemer

Aplikasi desktop otomatisasi untuk menukarkan (redeem) kode gift/promo game **Where Winds Meet** secara massal dengan antarmuka modern, aman, dan mudah digunakan.

![Platform](https://img.shields.io/badge/Platform-Windows-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen)
![UI](https://img.shields.io/badge/UI-CustomTkinter-blueviolet)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Fitur Utama

- **🚀 Mass / Batch Redeeming**: Masukkan puluhan kode sekaligus, aplikasi akan menginput dan menukarkannya secara berurutan.
- **🎯 Kalibrasi Koordinat Interaktif**: Menyesuaikan letak tombol input kode, tombol konfirmasi, dan tombol tutup sesuai resolusi layar Anda.
- **⏱️ Configurable Delays & Countdown**: Atur waktu jeda antar klik dan waktu jeda countdown sebelum otomatisasi berjalan agar Anda sempat berpindah (Alt-Tab) ke layar game.
- **🛡️ Run as Admin Detection**: Memastikan aplikasi berjalan dengan hak administrator agar automasi mouse dan keyboard dapat berinteraksi mulus dengan window game.
- **💾 Riwayat Penukaran Otomatis (SQLite)**: Riwayat kode yang sudah berhasil atau gagal disimpan rapi di database lokal sehingga tidak akan menukarkan kode yang sama dua kali.
- **🔔 Notifikasi Suara (Chime Alert)**: Suara nada sukses saat kode selesai ditukarkan dan nada pemberitahuan ketika proses berhenti.
- **🎨 Modern Dark Mode UI**: Tampilan elegan berbasis `CustomTkinter` yang nyaman dipandang.
- **🌐 Dukungan Multi-Bahasa**: Pilihan Bahasa Indonesia dan Bahasa Inggris.
- **🛑 Emergency Stop**: Tekan tombol darurat (`ESC` atau `F8`) kapan saja untuk menghentikan proses otomatisasi secara instan.

---

## 📥 Cara Menggunakan

Terdapat dua cara untuk menjalankan aplikasi ini:

### 🌟 Opsi 1: Download File Standalone `.exe` (Rekomendasi - Tanpa Install Python)
1. Pergi ke menu [**Releases**](https://github.com/Mahargip/wherewindsmeet_autoredeemer/releases) di repository GitHub ini.
2. Unduh file `WhereWindsMeet_AutoRedeemer.exe` versi terbaru.
3. Klik kanan pada file `.exe`, lalu pilih **Run as Administrator** *(Wajib agar simulasi klik dapat masuk ke game)*.
4. Aplikasi siap digunakan!

---

### 🛠️ Opsi 2: Menjalankan dari Source Code (Python)

Jika Anda ingin menjalankan atau memodifikasi kodenya secara langsung:

1. **Clone repository ini:**
   ```bash
   git clone https://github.com/Mahargip/wherewindsmeet_autoredeemer.git
   cd wherewindsmeet_autoredeemer
   ```

2. **Install dependensi yang dibutuhkan:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan aplikasi:**
   ```bash
   python app.py
   ```
   *(Atau double click `run_as_admin.bat`)*

---

## 📖 Panduan Langkah demi Langkah di Dalam Game

1. Buka game **Where Winds Meet** dan masuk ke menu **Redeem Code** (Penukaran Kode).
2. Jalankan **Where Winds Meet Auto Redeemer** sebagai Administrator.
3. Masukkan daftar kode redeem pada kolom teks (satu baris untuk setiap kode).
4. Klik tombol **Ambil Posisi** untuk melakukan kalibrasi:
   - **Posisi 1**: Kolom input teks kode redeem.
   - **Posisi 2**: Tombol konfirmasi / "Tukar" (Exchange/Redeem).
   - **Posisi 3**: Tombol konfirmasi hadiah / tombol tutup pop-up (opsional).
5. Tentukan waktu countdown (misal 5 detik).
6. Klik **Mulai**. Segera pindah (Alt-Tab) ke jendela game Anda sebelum countdown habis.
7. Biarkan aplikasi bekerja sampai seluruh kode selesai ditukarkan!

---

## 🔨 Cara Build Sendiri ke `.EXE`

Jika Anda telah melakukan perubahan pada script `app.py` dan ingin mengemasnya kembali menjadi file `.exe`:

1. Pastikan PyInstaller sudah terpasang:
   ```bash
   pip install pyinstaller
   ```
2. Cukup jalankan script batch build:
   ```cmd
   build_exe.bat
   ```
3. File `.exe` baru akan otomatis dibuat di folder `dist/` dan di root folder.

---

## ⚠️ Disclaimer

Aplikasi ini adalah alat bantu otomatisasi input (makro mouse & keyboard simulasi standar) untuk mempermudah pemain memasukkan banyak kode promo. Aplikasi ini **TIDAK** memodifikasi file game, memori, atau menginjeksi DLL ke dalam client game. Gunakan dengan bijak sesuai kenyamanan Anda.
