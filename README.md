# 🛒 ETL Pipeline: Fashion Studio Competitor Analysis

Sebuah proyek *Data Engineering* modular untuk melakukan ekstraksi, transformasi, dan pemuatan data (ETL) katalog produk kompetitor. Proyek ini dibangun sebagai *submission* tingkat **Advanced** untuk kelas **Belajar Fundamental Pemrosesan Data** di Dicoding.

## 📌 Fitur Utama (Sesuai Rubrik Advanced)

1. **Extract (`utils/extract.py`)**: 
   - Melakukan *web scraping* secara otomatis pada katalog `https://fashion-studio.dicoding.dev` (Halaman 1-50, target ~1000 data).
   - Menarik atribut: *Title, Price, Rating, Colors, Size, Gender*.
   - Menyertakan kolom `timestamp` presisi saat data ditarik.
   - Dilengkapi *error handling* (`try-except`) untuk mendeteksi kegagalan jaringan (*RequestException*).

2. **Transform (`utils/transform.py`)**:
   - Pembersihan ketat: menghapus data duplikat, baris *null* (`dropna`), dan data invalid (seperti "Unknown Product").
   - Konversi dan Standardisasi: 
     - Mengonversi mata uang `Price` ke IDR (asumsi kurs Rp16.000).
     - Standardisasi tipe data `Rating` menjadi *float*, serta ekstraksi numerik murni untuk `Colors`.
     - *Parsing* teks bersi pada kolom `Size` dan `Gender`.
   - Menggunakan validasi blok `try-except` eksplisit dalam fungsi *type casting* untuk menahan potensi *ValueError* atau *TypeError*.

3. **Load (`utils/load.py`)**:
   - Mengunggah data bersih secara konkuren ke **3 Repositori Data**:
     1. **Flat File**: Berkas `products.csv` lokal.
     2. **Database Relasional**: PostgreSQL.
     3. **Cloud Spreadsheet**: Google Sheets via API.
   - Dilengkapi penanganan *error* untuk kegagalan koneksi *database* maupun limitasi API.

4. **Unit Testing & Coverage**:
   - Diuji menggunakan `pytest` dengan implementasi *Mock testing* untuk isolasi proses *request* HTTP dan koneksi *database*.
   - Mencapai **Test Coverage 91%** (Syarat Advanced: 80-100%).

---

## 📂 Struktur Repositori

Proyek ini menerapkan prinsip *Modular Code* untuk kemudahan *maintenance* dan *testing*:
```text
simple-etl/
├── tests/
│   ├── test_extract.py      # Pengujian unit untuk fase Extract
│   ├── test_transform.py    # Pengujian unit untuk fase Transform
│   └── test_load.py         # Pengujian unit untuk fase Load
├── utils/
│   ├── extract.py           # Modul ekstraksi data (Scraping)
│   ├── transform.py         # Modul pembersihan & transformasi (Pandas)
│   └── load.py              # Modul penyimpanan ke CSV, DB, dan Sheets
├── main.py                  # Skrip orkestrator (titik eksekusi utama)
├── requirements.txt         # Daftar pustaka dependency
├── submission.txt           # Catatan instruksi untuk reviewer
├── products.csv             # Hasil akhir data (Flat file)
├── google-sheets-api.json   # Kredensial Service Account (Private)
└── README.md                # Dokumentasi proyek
```

⚙️ Prasyarat (Prerequisites)
Pastikan sistem Anda telah terinstal:

Python 3.9+

PostgreSQL (aktif di lokal atau server cloud)

Akses kredensial Google Service Account API (google-sheets-api.json)

Install semua library yang dibutuhkan dengan perintah berikut:


```Bash
pip install -r requirements.txt
```

🚀 Cara Menjalankan Proyek
1. Eksekusi Skrip ETL Utama
Jalankan file orkestrator untuk memulai siklus Extract, Transform, dan Load dari awal hingga akhir.

```Bash
python3 main.py
2. Menjalankan Unit Test
Proyek ini divalidasi menggunakan skenario unit test di dalam folder tests/. Jalankan perintah berikut untuk menguji seluruh fungsi:
```
```Bash
python3 -m pytest tests/
3. Memeriksa Test Coverage
Untuk memvalidasi cakupan baris kode yang teruji (harus di atas 80% untuk nilai maksimal):
```
```Bash
coverage run -m pytest tests/
coverage report -m
📊 Repositori Target (Google Sheets)
Hasil akhir pipeline ini dapat ditinjau secara langsung (secara live) pada tautan Google Sheets berikut:
```
[https://docs.google.com/spreadsheets/d/1nOMgE4U1KVB4tZqxR6oRCkQ5zZKfTs8RBI1zioNrwvU/edit?usp=sharing](https://docs.google.com/spreadsheets/d/1nOMgE4U1KVB4tZqxR6oRCkQ5zZKfTs8RBI1zioNrwvU/edit?usp=sharing)

✒️ Pengembang

Haikal Fairuzi Maulana
Dibuat untuk memenuhi kriteria submission "Membangun ETL Pipeline" - Dicoding Academy (2026).
