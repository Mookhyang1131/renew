import os
import sys
import json
import time
import requests

# --- Langkah 1: Baca Kredensial dari GitHub Secrets ---
# Kode ini mengambil data sensitif yang sudah Anda simpan di Settings > Secrets.
# Jika salah satu secret tidak ada, skrip akan berhenti dengan pesan error.
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
# REFRESH_TOKEN hanya digunakan saat skrip dijalankan pertama kali.
INITIAL_REFRESH_TOKEN = os.environ.get('REFRESH_TOKEN')

if not all([CLIENT_ID, CLIENT_SECRET, INITIAL_REFRESH_TOKEN]):
    print("❌ Error: Pastikan CLIENT_ID, CLIENT_SECRET, dan REFRESH_TOKEN sudah diatur di GitHub Secrets.")
    sys.exit(1)

# Lokasi file untuk menyimpan refresh token yang selalu baru.
TOKEN_FILE_PATH = 'Secret.txt'

# --- Langkah 2: Fungsi untuk Mendapatkan Token Baru ---
def get_new_token(refresh_token):
    """Menukar refresh token lama dengan access token dan refresh token yang baru."""
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': 'http://localhost:53682/'
    }
    
    print("🔄 Mencoba mendapatkan token baru dari Microsoft...")
    response = requests.post('https://login.microsoftonline.com/common/oauth2/v2.0/token', data=data, headers=headers)
    
    if response.status_code != 200:
        print(f"🔥 Gagal mendapatkan token. Status: {response.status_code}, Pesan: {response.text}")
        sys.exit(1)
    
    print("✅ Token baru berhasil didapatkan!")
    token_data = response.json()
    
    # Simpan refresh token yang BARU ke dalam file untuk digunakan di eksekusi berikutnya.
    with open(TOKEN_FILE_PATH, 'w') as f:
        f.write(token_data['refresh_token'])
    
    return token_data['access_token']

# --- Langkah 3: Fungsi Utama untuk Menjalankan Panggilan API ---
def main():
    """Fungsi utama untuk menjalankan seluruh proses."""
    
    print(f"🕰️  Memulai eksekusi pada: {time.asctime()}")
    
    # Jika Secret.txt tidak ada (eksekusi pertama kali), buat dari INITIAL_REFRESH_TOKEN.
    if not os.path.exists(TOKEN_FILE_PATH):
        print(f"File '{TOKEN_FILE_PATH}' tidak ditemukan. Membuat baru dari GitHub Secret.")
        with open(TOKEN_FILE_PATH, 'w') as f:
            f.write(INITIAL_REFRESH_TOKEN)

    # Baca refresh token dari file.
    with open(TOKEN_FILE_PATH, 'r') as f:
        current_refresh_token = f.read().strip()
        
    # Dapatkan access token yang valid untuk sesi ini.
    access_token = get_new_token(current_refresh_token)
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Daftar API endpoint yang akan dipanggil.
    api_endpoints = [
        'https://graph.microsoft.com/v1.0/me/drive/root',
        'https://graph.microsoft.com/v1.0/me/messages',
        'https://graph.microsoft.com/v1.0/me/mailFolders',
        'https://graph.microsoft.com/v1.0/me/outlook/masterCategories'
    ]
    
    print("\n🚀 Memulai panggilan API...")
    success_count = 0
    for i, endpoint in enumerate(api_endpoints, 1):
        try:
            response = requests.get(endpoint, headers=headers)
            if response.status_code == 200:
                print(f"  - Panggilan {i}/{len(api_endpoints)} ke endpoint berhasil (Status: 200 OK)")
                success_count += 1
            else:
                print(f"  - Panggilan {i}/{len(api_endpoints)} ke endpoint GAGAL (Status: {response.status_code})")
        except Exception as e:
            print(f"  - Panggilan {i}/{len(api_endpoints)} ke endpoint GAGAL karena error: {e}")

    print(f"\n✨ Eksekusi selesai. Total panggilan sukses: {success_count}/{len(api_endpoints)}")

# Menjalankan fungsi main saat skrip dieksekusi.
if __name__ == '__main__':
    main()
