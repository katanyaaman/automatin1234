import os
import json
import hmac
import hashlib
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Ambil VERIFY_TOKEN dari environment variable, dengan nilai default jika tidak ada.
VERIFY_TOKEN = os.getenv('FB_VERIFY_TOKEN', 'kmzwa8awaa')
# Ambil APP_SECRET dari environment variable. Ini WAJIB untuk verifikasi signature.
APP_SECRET = os.getenv('FB_APP_SECRET')
# Tentukan apakah kita dalam mode development (misalnya, jika variabel ini di-set ke 'true')
IS_DEVELOPMENT = os.getenv('VERCEL_ENV') == 'development'

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        """Menangani permintaan verifikasi dari Facebook (GET)."""
        print("GET request received for verification.")
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)

        # Ambil parameter dengan aman, berikan None jika tidak ada
        mode = query_params.get('hub.mode', [None])[0]
        token = query_params.get('hub.verify_token', [None])[0]
        challenge = query_params.get('hub.challenge', [None])[0]

        print(f"Mode: {mode}, Token: {token}, Challenge: {challenge}")

        # Pastikan semua parameter yang dibutuhkan ada
        if mode == 'subscribe' and token == VERIFY_TOKEN and challenge:
            print('Webhook verified successfully.')
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(challenge.encode('utf-8'))
        else:
            print('Verification failed: Token mismatch or invalid mode.')
            self.send_response(403)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Verification failed')
        return

    def do_POST(self):
        """Menangani event webhook yang masuk dari Facebook (POST)."""
        # 1. Baca body permintaan terlebih dahulu
        content_length = int(self.headers['Content-Length'])
        # Simpan body ke self.body agar bisa diakses oleh fungsi is_valid_signature
        self.body = self.rfile.read(content_length)

        # 2. Verifikasi Signature Permintaan (Sangat Penting untuk Keamanan)
        signature = self.headers.get('X-Hub-Signature-256')
        if not self.is_valid_signature(signature):
            print("ERROR: Invalid signature. Request rejected.")
            self.send_response(403)
            self.end_headers() # Cukup end_headers, tidak perlu kirim body
            return

        print("POST request received with valid signature.")

        # 3. Proses data JSON karena body sudah dibaca
        data = json.loads(self.body)

        print(f"Received data: {json.dumps(data, indent=2)}")

        # 3. Logika untuk memproses pesan
        if data.get('object') == 'page':
            for entry in data.get('entry', []):
                for messaging_event in entry.get('messaging', []):
                    if 'message' in messaging_event and 'text' in messaging_event['message']:
                        sender_id = messaging_event['sender']['id']
                        message_text = messaging_event['message']['text']
                        print(f'Received message from {sender_id}: {message_text}')
                        # TODO: Tambahkan logika bot Anda untuk membalas pesan di sini.

        # 5. Kirim respons 200 OK untuk memberitahu Facebook bahwa event telah diterima
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Event Received')
        return

    def is_valid_signature(self, signature):
        """Memvalidasi signature X-Hub-Signature-256."""
        if not signature:
            print("Signature not found in headers.")
            return False
        if not APP_SECRET:
            print("WARNING: FB_APP_SECRET is not set. Skipping signature validation.")
            # Hanya lewati validasi jika dalam mode development Vercel.
            # Di produksi, ini akan mengembalikan False dan menolak permintaan.
            return IS_DEVELOPMENT

        sha_name, signature_hash = signature.split('=', 1)
        if sha_name == 'sha256':
            expected_hash = hmac.new(APP_SECRET.encode(), self.body, hashlib.sha256).hexdigest()
            return hmac.compare_digest(expected_hash, signature_hash)
        return False