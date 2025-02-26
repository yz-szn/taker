# Taker Bot

Taker Bot adalah sebuah script otomatisasi untuk berbagai tugas terkait blockchain. 

## 1. Clone Repositori
Jalankan perintah berikut di terminal:

```sh
git clone https://github.com/yz-szn/taker.git
cd taker
```

## 2. Instalasi Dependensi
Pastikan Python 3.6 atau lebih baru sudah terinstal. Kemudian, jalankan:

```sh
pip install -r requirements.txt
```

## 3. Menjalankan Bot
Untuk menjalankan bot, gunakan perintah:

```sh
py run.py
```

## 4. Konfigurasi Wallet
Pastikan file `wallet.txt` berisi daftar alamat dan private key dengan format berikut:

```
address1:privatekey1
address2:privatekey2
address3:privatekey3
```
Ketika pertama kali menjalankan script, wajib menjalankan wallet converter terlebih dahulu untuk memastikan format wallet yang benar.
