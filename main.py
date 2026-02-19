from flask import Flask, request, jsonify
import datetime
import json
import os
import subprocess

app = Flask(__name__)
DATA_FILE = 'data.json'

def push_to_github():
    """Sinkronisasi ke GitHub dengan fitur perbaikan otomatis jika bentrok"""
    try:
        # Identitas Git
        subprocess.run(["git", "config", "user.email", "yudi02012001@gmail.com"], check=True)
        subprocess.run(["git", "config", "user.name", "YudiGetHub"], check=True)

        # Tambahkan file utama dashboard saja
        subprocess.run(["git", "add", "data.json", "index.html", "vercel.json", ".gitignore"], check=True)

        # Cek perubahan
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not status.stdout:
            print(">>> INFO: Data sudah sinkron.", flush=True)
            return

        # Commit perubahan
        subprocess.run(["git", "commit", "-m", f"Dashboard Update: {datetime.datetime.now()}"], check=True)

        # Coba push normal
        result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)

        if result.returncode != 0:
            print(">>> Terdeteksi bentrok, melakukan push paksa...", flush=True)
            subprocess.run(["git", "push", "origin", "main", "--force"], check=True)

        print(">>> SUKSES: Data tersinkron ke GitHub!", flush=True)
    except Exception as e:
        print(f" >>> LOG GIT: {e}", flush=True)

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f: return json.load(f)
        except: return []
    return []

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def home():
    return "Server Utama Replit Yudi Aktif!"

@app.route('/kirim-notif', methods=['POST'])
def terima_notif():
    print("\n--- TRANSAKSI MASUK ---", flush=True)
    data = request.get_json(force=True)
    pesan = data.get('isi_notif', 'Transaksi Baru')

    kategori = "PENGELUARAN"
    if any(x in pesan.lower() for x in ["masuk", "terima", "plus", "kredit", "topup"]):
        kategori = "PEMASUKAN"

    catatan = load_data()
    entry = {"waktu": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "tipe": kategori, "pesan": pesan}
    catatan.append(entry)
    save_data(catatan)

    # Menampilkan log singkat di console
    print(f"[{entry['waktu']}] {entry['tipe']}: {entry['pesan'][:30]}...", flush=True)

    # Sinkronisasi
    push_to_github()

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
