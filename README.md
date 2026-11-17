# SystemBot Ultimate - Bot Telegram Manajemen STB & Linux Server

**SystemBot Ultimate** adalah bot Telegram berbasis Python yang dirancang untuk mengelola, mengontrol, dan memantau STB (*Set Top Box* berbasis Armbian Linux) maupun server Linux lainnya dari jarak jauh. 

Proyek ini dibangun dengan fokus utama pada **aksesibilitas tinggi**, sehingga sangat nyaman dan intuitif digunakan dengan pembaca layar (*screen reader*) seperti **NVDA**, **JAWS**, maupun **TalkBack**.

---

## Fitur Utama

- **Aksesibilitas Penuh (Screen Reader Friendly):** Seluruh antarmuka tombol keyboard dan pesan teks diformat bersih, ringkas, dan bebas karakter dekoratif yang mengganggu pembaca layar.
- **Mode Shell Interaktif:** Memungkinkan eksekusi perintah terminal Linux langsung dari ruang obrolan Telegram.
- **Panel Kontrol Darurat:** Tombol pintas inline keyboard untuk mengirim sinyal terminal penting (`Ctrl+C`, `Ctrl+D`, `Ctrl+X`, `Ctrl+Z`, `Tab`, `ESC`, dan `Enter Manual`).
- **Sistem Rem & Konfirmasi Keamanan:** Tombol kritis seperti *Mulai Ulang Server (Reboot)* dan *Matikan Server (Power Off)* dilengkapi dialog konfirmasi (*Yes/Cancel*) untuk mencegah salah pencet.
- **Dukungan Dwibahasa (Bilingual):** Mendukung Bahasa Indonesia dan Bahasa Inggris secara penuh melalui perintah `/lang`.
- **Perintah Kustom Dinamis:** Pengguna dapat menambah dan menghapus tombol perintah Linux favorit mereka sendiri langsung dari menu Telegram tanpa perlu mengedit kode sumber.
- **Koneksi SSH Async & Tahan Putus:** Menggunakan library Paramiko dan asyncio untuk koneksi cepat dan penanganan pemulihan koneksi otomatis.

---

## Persyaratan Sistem

- Python versi 3.10 atau yang lebih baru.
- Sistem operasi Linux (direkomendasikan Armbian, Debian, atau Ubuntu).
- Paket SSH Server (`openssh-server`) aktif di perangkat target.

---

## Panduan Instalasi Cepat

### 1. Salin Repositori
```bash
git clone https://github.com/subhansyahbana/server_manager.git
cd server_manager
```

### 2. Pasang Dependensi
Pasang pustaka Python yang dibutuhkan:
```bash
pip3 install -r requirements.txt
```

### 3. Menjalankan Bot & Pengaturan Konfigurasi

Anda dapat mengatur konfigurasi dengan dua cara:

#### Metode A: Panduan Otomatis dari Terminal (Paling Mudah)
Cukup langsung jalankan bot di terminal:
```bash
python3 main.py
```
Jika file `config.json` belum ada atau belum diisi, bot akan **secara otomatis membuka wizard interaktif di terminal**:
1. Masukkan Token bot Telegram Anda.
2. Masukkan Telegram Chat ID Anda.
3. Masukkan Host SSH (cukup tekan `Enter` untuk default: `localhost`).
4. Masukkan Port SSH (cukup tekan `Enter` untuk default: `22`).
5. Masukkan Username SSH (cukup tekan `Enter` untuk default: `root`).
6. Masukkan Password SSH server/STB Anda.

File `config.json` akan otomatis dibuat dan disimpan, lalu bot langsung aktif! Untuk menjalankan di waktu berikutnya, bot akan langsung membaca `config.json` tanpa menanyakan ulang.

---

#### Metode B: Pengaturan Manual (Opsional)
Jika ingin membuat/mengedit file konfigurasi sendiri terlebih dahulu, buat atau edit file `config.json` (bisa mencontoh `config.example.json`):
```json
{
    "TOKEN": "MASUKKAN_TOKEN_BOT_DI_SINI",
    "AUTHORIZED_CHAT_ID": 123456789,
    "SSH_HOST": "localhost",
    "SSH_PORT": 22,
    "SSH_USER": "root",
    "SSH_PASSWORD": "password_stb_anda"
}
```

**Keterangan Parameter:**
- `TOKEN`: Token bot yang diperoleh dari [@BotFather](https://t.me/BotFather) di Telegram.
- `AUTHORIZED_CHAT_ID`: ID angka Telegram Anda untuk membatasi hak akses agar hanya Anda yang bisa mengontrol bot (cek via [@userinfobot](https://t.me/userinfobot)).
- `SSH_HOST`: Gunakan `"localhost"` jika bot berjalan langsung di server/STB target, atau isi alamat IP lokal jika bot dijalankan dari perangkat lain.
- `SSH_PORT`: Port SSH (standar: `22`).
- `SSH_USER` & `SSH_PASSWORD`: Kredensial login SSH ke Linux Anda.

Setelah selesai mengisi, jalankan bot:
```bash
python3 main.py
```
Setelah bot berhasil berjalan di terminal, buka Telegram dan kirim pesan `/start`.

---

## Menjalankan Otomatis di Latar Belakang (Systemd Service)

Agar bot tetap aktif di latar belakang dan otomatis berjalan kembali saat STB menyala ulang:

1. Buat file service systemd:
   ```bash
   sudo nano /etc/systemd/system/telegram-bot.service
   ```

2. Masukkan konfigurasi berikut (sesuaikan path folder jika berbeda):
   ```ini
   [Unit]
   Description=Bot Telegram Manajemen STB
   After=network.target

   [Service]
   ExecStart=/usr/bin/python3 /root/systembot/main.py
   WorkingDirectory=/root/systembot
   Restart=always
   User=root

   [Install]
   WantedBy=multi-user.target
   ```

3. Aktifkan dan jalankan service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable telegram-bot.service
   sudo systemctl start telegram-bot.service
   ```

---

## Daftar Perintah Telegram

- `/start` - Menampilkan dan menginisialisasi menu utama.
- `/lang` - Mengubah bahasa antarmuka (Bahasa Indonesia / English).
- `/help` - Menampilkan pesan panduan bantuan bot.
- `/ssh <perintah>` - Eksekusi cepat satu baris perintah Linux (misal: `/ssh uptime`).
- `/keyboard` - Memunculkan panel tombol kontrol darurat terminal (Ctrl+C, Tab, ESC, dll.).

---

## Lisensi & Kontribusi

Proyek ini bersifat terbuka (*open-source*). Kontribusi berupa saran, pelaporan kendala (*issue*), maupun perbaikan kode (*pull request*) sangat dipersilakan.
