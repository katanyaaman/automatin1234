# automationplusdhai

## Deskripsi
Proyek ini adalah alat otomatisasi untuk pengujian chatbot di berbagai platform, termasuk Webchat, Telegram, Instagram, dan sekarang Facebook Messenger.

## Fitur
- Pengujian otomatis pertanyaan dan respons
- Integrasi dengan LLM untuk penilaian
- Pembuatan laporan
- Penanganan error dan logging

## Persyaratan
- Python 3.x
- Dependensi: Lihat `requirements.txt`

## Instalasi
1. Clone repository
2. Instal dependensi: `pip install -r requirements.txt`

## Penggunaan
Jalankan `main.py` dengan environment variables yang sesuai:
- `PLATFORM`: webchat, telegram, instagram, facebook
- `FILENAME`: Path ke file data pengujian
- `TARGET_USERNAME`: Untuk platform seperti Telegram/Instagram/Facebook
- `FB_PAGE_ID`, `FB_ACCESS_TOKEN`: Untuk Facebook

Contoh:
```
set PLATFORM=facebook
set FB_PAGE_ID=your_page_id
set FB_ACCESS_TOKEN=your_access_token
set TARGET_USERNAME=target_user_id
python main.py
```

## Integrasi Facebook Messenger
- Menggunakan API resmi Meta Graph API
- Autentikasi dengan long-lived access token
- Dukungan webhook untuk penerimaan pesan (lihat webhook.py)
- Penanganan error dan logging

Catatan: Set environment variables seperti FB_PAGE_ID, FB_ACCESS_TOKEN, FB_APP_ID, FB_APP_SECRET. Gunakan long-lived tokens untuk sesi sekali pakai.