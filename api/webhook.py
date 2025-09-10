import os
import hmac
import hashlib
from flask import Flask, request

print("Webhook script started!") # Tambahkan baris ini untuk debugging

app = Flask(__name__)

# Ganti dengan VERIFY_TOKEN Anda dari pengaturan webhook Meta
VERIFY_TOKEN = os.getenv('FB_VERIFY_TOKEN', 'kmzwa8awaa')

@app.route('/webhook', methods=['GET'])
def verify():
    print("Verify function called.")
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    print(f"Mode: {mode}, Token: {token}, Challenge: {challenge}")

    if mode == 'subscribe' and token == VERIFY_TOKEN:
        print('Webhook verified successfully.')
        return challenge, 200
    else:
        print('Verification failed: Token mismatch or invalid mode.')
        return 'Verification failed', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    print("Webhook POST function called.")
    data = request.get_json()
    print(f"Received data: {data}")
    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                if messaging_event.get('message'):
                    sender_id = messaging_event['sender']['id']
                    message_text = messaging_event['message']['text']
                    print(f'Received message from {sender_id}: {message_text}')
                    # Di sini, integrasikan dengan logika bot Anda
    return 'Event Received', 200