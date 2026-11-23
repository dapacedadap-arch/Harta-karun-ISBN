# 🏴‍☠️ Peta Harta ISBN

Aplikasi web untuk memvalidasi nomor **ISBN-10** dan **ISBN-13** menggunakan **aritmetika modulo**, dibuat dengan Python dan Streamlit bertema laut dan bajak laut.

Proyek mata kuliah Matematika Diskrit
**Tsaqif Fadhlurrohman (F1E126019)**

## Konsep

ISBN memiliki **digit pemeriksa** (check digit) di posisi terakhir untuk mendeteksi kesalahan ketik.

| Jenis | Bobot | Syarat valid |
|---|---|---|
| ISBN-10 | 10, 9, 8, …, 1 | Jumlah berbobot habis dibagi **11** (digit akhir boleh `X` = 10) |
| ISBN-13 | 1, 3, 1, 3, … | Jumlah berbobot habis dibagi **10** |

Contoh: `0-306-40615-2` → jumlah berbobot 132 → 132 mod 11 = 0 → **valid**.

## Fitur

- **Periksa**: deteksi otomatis ISBN-10 atau ISBN-13, lengkap dengan tabel perhitungan digit × bobot dan hasil modulonya.
- **Cari Digit**: menghitung digit pemeriksa dari 9 atau 12 digit awal.
- **Ubah 10→13**: konversi ISBN-10 ke ISBN-13 dengan awalan 978.
- **Peti Riwayat**: daftar semua ISBN yang sudah diperiksa.
- Tema laut dengan gambar latar, dekorasi bergerak, dan maskot yang berkomentar sesuai hasil.

## Cara menjalankan

1. Pasang Python 3.10 atau yang lebih baru.
2. Pasang library yang dibutuhkan:
   ```
   pip install -r requirements.txt
   ```
3. Jalankan aplikasi dari folder proyek:
   ```
   python -m streamlit run "projek matdis.py"
   ```
4. Buka `http://localhost:8501` di browser.

## Struktur folder

```
├── projek matdis.py     # kode aplikasi
├── requirements.txt     # daftar library
├── latar.jpg            # gambar latar (opsional)
├── maskot1.jpg          # maskot di jendela kapal (opsional)
├── maskot2.png          # maskot penjaga (opsional)
└── dekorasi/            # hiasan bergerak (opsional)
```

Gambar bersifat opsional: tanpa gambar, aplikasi tetap berjalan dengan latar gradasi laut.

## Teknologi

Python · Streamlit · pandas · HTML/CSS
