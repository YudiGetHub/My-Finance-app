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
        # MEMAKSA IDENTITAS GIT DARI DALAM KODE
        # Ini untuk mengatasi error "Author identity unknown" secara permanen
        subprocess.run(["git", "config", "user.email", "yudi02012001@gmail.com"], check=True)
        subprocess.run(["git", "config", "user.name", "YudiGetHub"], check=True)

        # 1. Menambahkan semua file ke antrean git
        subprocess.run(["git", "add", "."], check=True)

        # 2. Membuat catatan commit
        subprocess.run(["git", "commit", "-m", f"Auto-update: {datetime.datetime.now()}"], check=True)

        # 3. Mengirim ke GitHub
        subprocess.run(["git", "push", "origin", "main"], check=True)

        print(">>> SUKSES: Data telah diperbarui di GitHub!", flush=True)
    except Exception as e:
        if "nothing to commit" in str(e).lower():
            print(">>> INFO: Tidak ada perubahan baru.", flush=True)
        else:
            print(f">>> GAGAL AUTOPUSH: {e}", flush=True)

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except: return []
    return []

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def home():
    return "Server Dashboard Yudi Aktif!"

@app.route('/kirim-notif', methods=['POST'])
def terima_notif():
    print("--- PROSES TRANSAKSI BARU ---", flush=True)
    data = request.get_json(force=True)
    pesan = data.get('isi_notif', 'Tes Transaksi')

    kategori = "PENGELUARAN"
    if any(x in pesan.lower() for x in ["masuk", "terima", "plus", "kredit", "topup", "berhasil"]):
        kategori = "PEMASUKAN"

    catatan = load_data()
    entry = {
        "waktu": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipe": kategori,
        "pesan": pesan
    }
    catatan.append(entry)
    save_data(catatan)

    # Jalankan sinkronisasi
    push_to_github()

    print(f"BERHASIL DICATAT: {entry}", flush=True)
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
