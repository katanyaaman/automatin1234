import os
import requests
import json
import time
import pickle
import os.path

class FacebookClient:
    """A client for interacting with the Facebook Messenger API.
    
    This class handles authentication, message sending, and message retrieval
    for a Facebook page using the Messenger API.
    """
    
    def __init__(self):
        """Initialize the Facebook client with necessary credentials and tokens."""
        self.access_token = None
        self.page_id = os.getenv('FB_PAGE_ID')
        self.token_file = 'fb_access_token.pickle'
        self.load_access_token()

    def load_access_token(self):
        """Load the access token from file or environment variables.
        
        First attempts to load a saved token from file. If not found,
        tries to get a short-lived token from environment variables and
        exchanges it for a long-lived token. As a fallback, looks for
        a pre-existing access token in environment variables.
        
        Raises:
            ValueError: If neither FB_ACCESS_TOKEN nor FB_SHORT_LIVED_TOKEN
                      environment variables are set.
        """
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as f:
                self.access_token = pickle.load(f)
            print("Loaded saved access token.")
        else:
            short_lived_token = os.getenv('FB_SHORT_LIVED_TOKEN')
            if short_lived_token:
                self.access_token = self.exchange_to_long_lived(short_lived_token)
                self.save_access_token()
            else:
                self.access_token = os.getenv('FB_ACCESS_TOKEN')
                if not self.access_token:
                    raise ValueError("FB_ACCESS_TOKEN or FB_SHORT_LIVED_TOKEN environment variable must be set.")
                self.save_access_token()

    def save_access_token(self):
        """Save the current access token to a file for future use."""
        with open(self.token_file, 'wb') as f:
            pickle.dump(self.access_token, f)
        print("Access token saved for future use.")

    def send_message(self, recipient_id, message):
        """Send a message to a specific recipient using the Messenger API.
        
        Args:
            recipient_id (str): The PSID of the message recipient.
            message (str): The text message to send.
            
        Returns:
            None
        """
        if not self.access_token:
            print("Access token not loaded. Cannot send message.")
            return
        url = f"https://graph.facebook.com/v20.0/{self.page_id}/messages"
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message},
            "messaging_type": "RESPONSE"
        }
        params = {"access_token": self.access_token}
        try:
            response = requests.post(url, params=params, json=payload)
            response.raise_for_status()
            print(f"Message sent to {recipient_id}: {message}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending message to {recipient_id}: {e}")

    def get_latest_message(self, conversation_id=None):
        """Retrieve the latest message from a conversation.
        
        Args:
            conversation_id (str, optional): The ID of the specific conversation.
                                          Currently unused, for future implementation.
            
        Returns:
            dict: A dictionary containing sender_id and message_text if successful,
                 None otherwise.
        """
        if not self.access_token:
            print("Access token not loaded. Cannot get messages.")
            return None
        # Polling sederhana untuk pesan terbaru; idealnya gunakan webhook
        url = f"https://graph.facebook.com/v20.0/{self.page_id}/conversations"
        params = {
            "access_token": self.access_token,
            "fields": "messages{from,message,created_time}"
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            # Ambil pesan terbaru (simplified)
            if data.get('data'):
                latest = data['data'][0]['messages']['data'][0]
                return {"sender_id": latest['from']['id'], "message_text": latest['message']}
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error getting latest message: {e}")
            return None

    def exchange_to_long_lived(self, short_lived_token):
        """Exchange a short-lived token for a long-lived one.
        
        Args:
            short_lived_token (str): The short-lived access token to exchange.
            
        Returns:
            str: The long-lived access token if successful, None otherwise.
        """
        url = "https://graph.facebook.com/v20.0/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": os.getenv('FB_APP_ID'),
            "client_secret": os.getenv('FB_APP_SECRET'),
            "fb_exchange_token": short_lived_token
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('access_token')
        except requests.exceptions.RequestException as e:
            print(f"Error exchanging token: {e}")
            return None