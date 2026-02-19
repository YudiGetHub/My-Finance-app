from flask import Flask, request, jsonify
import datetime
import json
import os
import subprocess

app = Flask(__name__)
DATA_FILE = 'data.json'

def push_to_github():
    try:
        # Menambah file, commit, dan push via command line
        subprocess.run(["git", "add", DATA_FILE])
        subprocess.run(["git", "commit", "-m", "Update data keuangan otomatis"])
        subprocess.run(["git", "push"])
        print("--- BERHASIL PUSH KE GITHUB ---")
    except Exception as e:
        print(f"Gagal Push: {e}")

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
    return "Server Keuangan Yudi Aktif & Terhubung GitHub!"

@app.route('/kirim-notif', methods=['POST'])
def terima_notif():
    print("--- ADA NOTIFIKASI BARU ---")
    data = request.get_json(force=True)
    pesan = data.get('isi_notif', 'Tes Notif')

    kategori = "PENGELUARAN"
    if any(x in pesan.lower() for x in ["masuk", "terima", "plus", "kredit"]):
        kategori = "PEMASUKAN"

    catatan = load_data()
    entry = {
        "waktu": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipe": kategori,
        "pesan": pesan
    }
    catatan.append(entry)
    save_data(catatan)

    # TRIGGER AUTO PUSH
    push_to_github()

    print(f"TERCATAT: {entry}")
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
