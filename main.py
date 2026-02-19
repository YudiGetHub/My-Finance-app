from flask import Flask, request, jsonify
import datetime
import json
import os
import subprocess
import sys

app = Flask(__name__)
DATA_FILE = 'data.json'

def push_to_github():
    """Fungsi otomatis mengirim semua perubahan ke GitHub setiap ada update"""
    try:
        # 1. Menambahkan semua file ke antrean git (termasuk index.html)
        subprocess.run(["git", "add", "."], check=True)

        # 2. Membuat catatan perubahan dengan waktu sekarang
        subprocess.run(["git", "commit", "-m", f"Auto-update: {datetime.datetime.now()}"], check=True)

        # 3. Memaksa push ke branch main di GitHub
        subprocess.run(["git", "push", "origin", "main"], check=True)

        print(">>> SUKSES: Data dan Dashboard telah diperbarui di GitHub!", flush=True)
    except Exception as e:
        print(f">>> GAGAL AUTOPUSH: {e}", flush=True)
        print("Saran: Pastikan kamu sudah melakukan Push manual sekali di tab Git Replit.", flush=True)

def load_data():
    """Memuat data dari file JSON"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except: 
            return []
    return []

def save_data(data):
    """Menyimpan data ke file JSON secara permanen"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def home():
    return "Server Dashboard Yudi Aktif! Cek link Vercel untuk grafik keuangan."

@app.route('/kirim-notif', methods=['POST'])
def terima_notif():
    # Menggunakan flush=True agar log muncul seketika di Console
    print("--- PROSES TRANSAKSI BARU DIMULAI ---", flush=True)

    data = request.get_json(force=True)
    pesan = data.get('isi_notif', 'Transaksi Uji Coba')

    # Logika deteksi otomatis tipe transaksi
    kategori = "PENGELUARAN"
    kata_kunci_masuk = ["masuk", "terima", "plus", "kredit", "topup", "penerimaan", "berhasil"]
    if any(x in pesan.lower() for x in kata_kunci_masuk):
        kategori = "PEMASUKAN"

    # Proses simpan data ke data.json
    catatan = load_data()
    entry = {
        "waktu": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipe": kategori,
        "pesan": pesan
    }
    catatan.append(entry)
    save_data(catatan)

    # Menjalankan fungsi otomatis kirim ke GitHub
    push_to_github()

    print(f"BERHASIL DICATAT: {entry}", flush=True)
    return jsonify({"status": "success", "github_updated": True}), 200

if __name__ == '__main__':
    # Menjalankan server Flask di port 8080
    app.run(host='0.0.0.0', port=8080)
