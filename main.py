from flask import Flask, request, jsonify
import datetime
import json
import os

app = Flask(__name__)
DATA_FILE = 'data.json'

# Fungsi untuk memuat data dari file
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

# Fungsi untuk menyimpan data ke file
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def home():
    return "Server Replit Yudi Aktif! Menunggu data dari MacroDroid..."

@app.route('/kirim-notif', methods=['POST'])
def terima_notif():
    # Mengambil data JSON yang dikirim MacroDroid
    incoming_data = request.json
    pesan_mentah = incoming_data.get('isi_notif', '')
    
    if not pesan_mentah:
        return jsonify({"status": "error", "message": "Pesan kosong"}), 400

    # Logika sederhana menentukan uang masuk/keluar
    kategori = "PENGELUARAN"
    kata_kunci_masuk = ["masuk", "terima", "plus", "kredit", "penerimaan"]
    if any(x in pesan_mentah.lower() for x in kata_kunci_masuk):
        kategori = "PEMASUKAN"

    # Simpan ke data.json
    catatan = load_data()
    entry = {
        "waktu": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipe": kategori,
        "pesan": pesan_mentah
    }
    catatan.append(entry)
    save_data(catatan)
    
    print(f"Data Baru Masuk: {entry}")
    return jsonify({"status": "success", "data": entry}), 200

if __name__ == '__main__':
    # Menjalankan server pada port 8080
    app.run(host='0.0.0.0', port=8080)
