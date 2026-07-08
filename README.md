# GenetikaAlgoritma

Aplikasi berbasis CLI (Command Line Interface) yang mencocokkan kosakata Bahasa Indonesia ke Bahasa Konjo menggunakan pendekatan **Algoritma Genetika (Genetic Algorithm)**. Program ini memuat dataset langsung dari file Excel dan melakukan simulasi proses evolusi (inisialisasi populasi, perhitungan fitness, seleksi roulette wheel, crossover, dan mutasi) untuk menemukan string target.

## 🚀 Fitur Aplikasi
* **Manajemen Kamus:** Memuat, menampilkan, dan mencari kosakata dari dataset Excel (`Dataset Kamus.xlsx`)[cite: 1].
* **Simulasi Algoritma Genetika Langkah demi Langkah:**
    * Perhitungan Nilai Fitness[cite: 1]
    * Seleksi Orang Tua (Roulette Wheel Selection)[cite: 1]
    * Proses Silang Sila (Crossover) & Mutasi[cite: 1]
    * Pembentukan Generasi Baru[cite: 1]

## 🛠️ Prasyarat & Instalasi
Pastikan Anda sudah menginstal Python (versi 3.x) dan pustaka yang diperlukan:
```bash
pip install pandas openpyxl
