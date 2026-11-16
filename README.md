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

### 3. Pengaturan Konfigurasi
Buka file `config.json` (atau salin dari `config.example.json`):
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

**Keterangan Pengaturan:**
- `TOKEN`: Token bot yang diperoleh dari [@BotFather](https://t.me/BotFather) di Telegram.
- `AUTHORIZED_CHAT_ID`: ID unik akun Telegram Anda untuk membatasi akses hanya kepada Anda (dapat dicek melalui [@userinfobot](https://t.me/userinfobot)).
- `SSH_HOST`: Gunakan `"localhost"` jika bot dijalankan langsung di dalam STB/Server, atau masukkan IP STB jika dijalankan dari luar.
- `SSH_PORT`: Port SSH (standar: 22).
- `SSH_USER` & `SSH_PASSWORD`: Kredensial login SSH ke perangkat Anda.

### 4. Jalankan Bot
```bash
python3 main.py
```
Setelah bot berjalan, buka Telegram dan kirim pesan `/start`.

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
