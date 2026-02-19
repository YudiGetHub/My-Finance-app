from flask import Flask, request, jsonify
import datetime
import json
import os
import subprocess

app = Flask(__name__)
DATA_FILE = 'data.json'

def push_to_github():
    """Fungsi otomatis mengirim semua perubahan ke GitHub setiap ada update"""
    try:
        # Menambahkan semua file (termasuk index.html dan data.json) ke antrean git
        subprocess.run(["git", "add", "."], check=True)
        # Membuat catatan perubahan dengan timestamp terbaru
        subprocess.run(["git", "commit", "-m", f"Update data & dashboard: {datetime.datetime.now()}"], check=True)
        # Mengirim ke GitHub - Ditambahkan 'origin main' agar lebih spesifik
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print(">>> SUKSES: Data dan Dashboard telah diperbarui di GitHub!")
    except subprocess.CalledProcessError as e:
        print(f">>> GAGAL PUSH: Pastikan kamu sudah push manual sekali lewat tombol Replit. Error: {e}")
    except Exception as e:
        print(f">>> ERROR SISTEM: {e}")

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
    # Mengarahkan pesan utama ke Dashboard
    return "Server Dashboard Yudi Aktif! Cek link Vercel kamu untuk melihat grafik."

@app.route('/kirim-notif', methods=['POST'])
def terima_notif():
    print("--- MENERIMA TRANSAKSI BARU ---")
    data = request.get_json(force=True)
    pesan = data.get('isi_notif', 'Transaksi Uji Coba')

    # Logika deteksi otomatis tipe transaksi
    kategori = "PENGELUARAN"
    kata_kunci_masuk = ["masuk", "terima", "plus", "kredit", "topup", "penerimaan", "berhasil"]
    if any(x in pesan.lower() for x in kata_kunci_masuk):
        kategori = "PEMASUKAN"

    # Proses simpan data
    catatan = load_data()
    entry = {
        "waktu": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipe": kategori,
        "pesan": pesan
    }
    catatan.append(entry)
    save_data(catatan)

    # Jalankan proses sinkronisasi ke GitHub secara otomatis
    push_to_github()

    print(f"BERHASIL DICATAT: {entry}")
    return jsonify({"status": "success", "github_updated": True}), 200

if __name__ == '__main__':
    # Menjalankan server Flask di port 8080
    app.run(host='0.0.0.0', port=8080)
