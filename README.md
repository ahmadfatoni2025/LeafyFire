# The Firebender AI (Fluid Edition)

Proyek Computer Vision yang menggunakan AI (Kecerdasan Buatan) terbaru dari Google (MediaPipe Tasks API) dan pemrosesan gambar matriks (OpenCV) untuk mengkonversi gerakan tangan Anda menjadi efek manipulasi api ultra-realistis secara real-time.

Alih-alih memproses ratusan "partikel titik" geometris yang membebani kinerja, proyek ini sepenuhnya menggunakan kalkulasi termodinamika simulasi Fluid Matrix. Program mampu merender "panas" secara berlapis, mulus, dan zero-lag, layaknya menguasai kendali elemen di dunia nyata.

---

## Fitur Utama

- Pelacakan Tangan Pintar (AI Brain): Mengekstrak pelacakan fitur lekukan, posisi, dan 5 ujung jari baik dari satu maupun dua belah tangan secara mulus melalui AI Google MediaPipe. 
- Fluid Fire Rendering: Sistem matriks aliran komputasi yang mencontoh wujud sifat suhu panas pada wujud ruang. Matriks membuat letupan mendingin dan merenggang ke atas dengan distorsi gelombang sinus yang sangat ringan bagi CPU Anda. 
- Custom Colour-Map: Gradasi palet spektrum api direpetisi sedetail mungkin (warna Gelap Pekat -> Merah Dalam -> Oranye Membara -> Kuning Terang -> hingga lapisan Putih di titik sumber pusat).
- Pemicu Jari Mengepal (Fist-Off): Deteksi geometrik menghentikan kobaran memudar ketika tangan Anda tertutup (mengepal rapat) lalu langsung siap mengobarkan panas lagi segera setelah kelimanya merentang terbuka.
- Iron Man Ultimate Explosions: Menyempurnakan efek sinematik. Dekatkan kedua tangan di layar untuk mengumpulkan cadangan energi sentral dan merentangkannya sejauh mungkin dengan spontan guna menghasilkan ledakan masif terang.

---

## Struktur File (Modular Architecture)

Program ini memisahkan kodenya agar ringkas, modular, dan lebih mudah digunakan atau dikembangkan:

- `main.py` : Entri titik untuk kamera dioperasikan dan efek hasil akhir diproyeksikan (UI dan status loop program ada di sini).
- `fire_effect.py` : Berisi komputasi ruang array Fisika Fluida Api untuk pengolahan pergeseran panas dalam memori matriks yang dirender secara optimal.
- `hand_tracker.py` : Abstraksi detektor dari model MediaPipe Tasks Vision API yang akan memastikan pendeteksian titik jari tangan yang ringkas secara konstan.
- `config.py` : Menyimpan parameter sistem, pengaturan kualitas hasil render layar (rasio skala), dan alamat model AI.

---

## Cara Instalasi

1. Pastikan Anda telah menginstal lingkungan perangkat Python 3.x pada komputer Anda.
2. Buka Terminal / command line dengan destinasi folder (direktori) di bawah ini lalu instal kebutuhan libraries:

```bash
pip install opencv-python mediapipe numpy
```

(Perhatian: Program ini memiliki script auto-download, skrip cerdas di `hand_tracker.py` akan memastikan mesin model milik Google sebesar kurang lebih 30MB di-unduh secara spesifik otomatis apabila absen dari mesin PC Anda saat diinisiasi di kali pertama).

---

## Cara Menjalankan

Luncurkan di baris terminal Anda:
```bash
python main.py
```

### Panduan Interaksi dan Kendali Hotkeys Aplikasi:
Kamera menyala:
- Tekan `C` : Siklus mengubah Style/Palet ras api (Classic Fire, Blue Flame, dan Green Inferno).
- Tekan `Q` : Untuk interupsi menutup jendela aplikasi secara tertutup dengan sempurna.
- Tangan Dibuka : Setiap tangan Anda otomatis meluapkan dan membakar atmosfer sekitar elemen ujung jari dan tengah tapak asalkan lengan dapat tertangkap dengan baik.
- Tangan Dikepal : Padamkan sekitarnya.
- Mode Energi Penuh: Mendekatkan kedua tangan terbuka dari kedua belah lengan untuk mempersiapkan titik simpul, lalu melebarkannya untuk memancarkan kilasan penuh.

---

## Catatan Resolusi Kamera
Jika diperlukan pembesaran/perampingan program silakan mengoreksi variabel berikut di dokumen `config.py`:
```python
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
```
Penting: Format ukuran natif bawaan yang ideal memuat 640x480, 1280x720, atau resolusi spesifik lainnya. Bila Anda memaksa ukuran ke yang tidak proporsional seperti 4000x6000 dan mendadak frame-skip atau aplikasi mogok berjalan (blackscreen); kembalikan kepada proporsi kamera rasio bawaan semula untuk memperbaiki fungsionalitasnya kembali.
