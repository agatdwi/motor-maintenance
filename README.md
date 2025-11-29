# 🏍️ Motor Maintenance Kelompok 2

Aplikasi desktop modern untuk mengelola jadwal perawatan motor dengan antarmuka yang intuitif dan fitur lengkap. Dibuat dengan Python dan CustomTkinter untuk pengalaman pengguna yang optimal.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-Latest-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Fitur Utama

### 🎯 Manajemen Servis
- ✅ **Jadwal Otomatis** - Hitung jadwal servis berdasarkan KM dan waktu
- 📊 **Progress Visual** - Progress bar lingkaran dengan warna status
- 🔔 **Notifikasi Real-time** - Peringatan servis yang sudah jatuh tempo
- 📱 **Multi Motor** - Kelola beberapa motor sekaligus

### 🎨 Antarmuka Modern
- 🎪 **Multiple Themes** - 4 pilihan tema warna yang cantik
- 📱 **Responsive Design** - Layout sidebar yang intuitif
- ✨ **Animasi Smooth** - Transisi dan highlight animasi
- 🎯 **Visual Feedback** - Warna status (hijau/kuning/merah)

### 🔧 Fitur Tambahan
- 💾 **Export Data** - Simpan riwayat servis ke CSV
- 🚀 **Simulasi KM** - Testing peningkatan KM otomatis
- 📋 **Riwayat Servis** - Catatan lengkap semua servis
- 🛠️ **Motor Custom** - Tambah motor dan servis custom

## 📸 Screenshots

### Tampilan Utama
![Dashboard](https://files.catbox.moe/0dii6t.png)

### Panel Servis
![Services](https://files.catbox.moe/msrbxj.png)

### Tema Berbeda
![Themes](https://files.catbox.moe/0fci2x.png)

## 🚀 Instalasi

### Prerequisites
- Python 3.8 atau lebih tinggi
- pip (Python package manager)

### Langkah Instalasi

1. **Clone repository**
```bash
git clone https://github.com/agatdwi/motor-maintenance.git
cd motor-maintenance
```

2. **Buat virtual environment (recommended)**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Jalankan aplikasi**
```bash
python maintenance_full.py
```

### 📦 Dependencies
Package yang diperlukan:
```text
customtkinter>=5.2.0
Pillow>=10.0.0
```

## 🎮 Cara Menggunakan

### 1. Pilih Motor
- Pilih motor dari dropdown list
- Motor preset: Honda Beat, Yamaha NMAX, Honda Vario 150
- Atau tambah motor custom dengan tombol "➕ Tambah Motor"

### 2. Input KM Saat Ini
- Masukkan kilometer motor saat ini
- KM digunakan untuk menghitung jadwal servis berikutnya

### 3. Kelola Servis
- Lihat status semua servis di panel utama
- Warna menunjukkan status:
  - 🟢 **Hijau**: Aman
  - 🟡 **Kuning**: Peringatan (hampir jatuh tempo)
  - 🔴 **Merah**: Terlambat

### 4. Tandai Servis Selesai
- Klik tombol "✅ Selesai" pada kartu servis
- Sistem akan otomatis menghitung jadwal berikutnya
- Riwayat akan tersimpan di database

## 🗂️ Struktur Database

Aplikasi menggunakan SQLite dengan 3 tabel utama:

### 📊 Tabel Motors
```sql
- id (INTEGER PRIMARY KEY)
- name (TEXT UNIQUE)
- created_at (TEXT)
```

### 🔧 Tabel Services
```sql
- id (INTEGER PRIMARY KEY)
- motor_name (TEXT)
- service_name (TEXT)
- interval_km (INTEGER)
- interval_bulan (INTEGER)
- next_due_km (INTEGER)
- next_due_date (TEXT)
- last_serviced_at (TEXT)
```

### 📋 Tabel History
```sql
- id (INTEGER PRIMARY KEY)
- motor_name (TEXT)
- service_name (TEXT)
- when_served (TEXT)
- km_at_service (INTEGER)
```

## 🎨 Kustomisasi

### Tambah Motor Baru
1. Klik "➕ Tambah Motor"
2. Isi nama motor
3. Tambah servis dengan interval KM dan bulan
4. Simpan ke database

### Ganti Tema
- Pilih tema dari dropdown di sidebar
- Tersedia 4 tema: Premium Dark, Gamer RGB, Minimal Clean, Sunset Orange

### Export Data
- Klik "📊 Export CSV" untuk simpan riwayat
- File CSV bisa dibuka di Excel/Google Sheets

## 🔧 Fitur Teknis

### Simulasi KM
- Testing otomatis peningkatan KM
- Kontrol kecepatan dengan slider
- Berguna untuk demo dan testing

### Auto-Check System
- Pengecekan otomatis setiap detik
- Notifikasi untuk servis yang jatuh tempo
- Progress bar update real-time

### Custom Widgets
- **AnimatedCard**: Kartu dengan efek highlight
- **CircularProgressBar**: Progress bar lingkaran

## 🐛 Troubleshooting

### Common Issues

1. **Aplikasi tidak bisa dibuka**
   - Pastikan Python 3.8+ terinstall
   - Jalankan `pip install -r requirements.txt`

2. **Database error**
   - Hapus file `motor_maintenance.db`
   - Aplikasi akan buat database baru

3. **Tampilan tidak proper**
   - Update CustomTkinter: `pip install --upgrade customtkinter`

### Reset Data
- Klik "Clear All (DB)" di panel aksi cepat
- **Warning**: Menghapus semua data permanen!

## 🤝 Kontribusi

Kontribusi sangat diterima! Ikuti langkah berikut:

1. Fork repository
2. Buat feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 Roadmap

- [ ] **Mobile App** - Versi Android/iOS
- [ ] **Cloud Sync** - Sync data antar perangkat
- [ ] **Backup/Restore** - Fitur backup data
- [ ] **Multiple Language** - Support bahasa lain
- [ ] **Report Analytics** - Laporan statistik servis

## 📄 Lisensi

Distributed under MIT License. See `LICENSE` for more information.

## 👨‍💻 Developer

Dibuat dengan ❤️ oleh [AgatZ]

- GitHub: [@agatdwi](https://github.com/agatdwi)
- Email: agatdwisubaktiyan444@gmail.com

## 🙏 Acknowledgments

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Untuk UI components yang modern
- [SQLite](https://www.sqlite.org) - Database engine yang reliable
- [Pillow](https://python-pillow.org) - Image processing capabilities

---

**⭐ Jangan lupa kasih star jika project ini membantu! ⭐**

---

## 📞 Support

Jika ada pertanyaan atau butuh bantuan:
1. Buka [Issues](https://github.com//agatdwi/motor-maintenance/issues) di GitHub
2. Email: agatdwisubaktiyan444@gmail.com

**Happy Riding! 🏍️✨**
