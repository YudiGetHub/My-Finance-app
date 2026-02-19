from flask import Flask, request, jsonify
import datetime
import json
import os
import subprocess

app = Flask(__name__)
DATA_FILE = 'data.json'

def push_to_github():
    """Fungsi otomatis mengirim data.json ke GitHub setiap ada update"""
    try:
        # Menambahkan file data.json ke antrean git
        subprocess.run(["git", "add", DATA_FILE], check=True)
        # Membuat catatan perubahan
        subprocess.run(["git", "commit", "-m", f"Update data: {datetime.datetime.now()}"], check=True)
        # Mengirim ke GitHub
        subprocess.run(["git", "push"], check=True)
        print(">>> DATA BERHASIL TERKIRIM KE GITHUB!")
    except subprocess.CalledProcessError as e:
        print(f">>> GAGAL PUSH: Mungkin perlu Push manual pertama kali via tombol Replit. Error: {e}")
    except Exception as e:
        print(f">>> ERROR LAIN: {e}")

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
    return "Server Yudi Aktif. Cek tab Code di GitHub untuk melihat data!"

@app.route('/kirim-notif', methods=['POST'])
def terima_notif():
    print("--- ADA TRANSAKSI MASUK ---")
    data = request.get_json(force=True)
    pesan = data.get('isi_notif', 'Tes Transaksi')

    # Deteksi otomatis uang masuk/keluar
    kategori = "PENGELUARAN"
    if any(x in pesan.lower() for x in ["masuk", "terima", "plus", "kredit", "topup"]):
        kategori = "PEMASUKAN"

    catatan = load_data()
    entry = {
        "waktu": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipe": kategori,
        "pesan": pesan
    }
    catatan.append(entry)
    save_data(catatan)

    # Jalankan proses kirim ke GitHub
    push_to_github()

    print(f"TERCATAT DI REPLIT & GITHUB: {entry}")
    return jsonify({"status": "success", "pushed": True}), 200

if __name__ == '__main__':
    # Server berjalan di port 8080
    app.run(host='0.0.0.0', port=8080)
