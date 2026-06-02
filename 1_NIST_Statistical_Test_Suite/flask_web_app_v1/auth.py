import os
import json
import requests
from urllib.parse import urlencode
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

class GoogleAuth:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = "https://accounts.google.com/o/oauth2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def get_authorization_url(self):
        """Generate Google OAuth authorization URL"""
        import secrets
        state = secrets.token_urlsafe(32)
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'openid email profile',
            'response_type': 'code',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        return auth_url, state
    
    def exchange_code_for_token(self, code, state):
        """Exchange authorization code for access token and user info"""
        try:
            # Exchange code for tokens
            token_data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri
            }
            
            token_response = requests.post(self.token_url, data=token_data)
            token_response.raise_for_status()
            tokens = token_response.json()
            
            if 'access_token' not in tokens:
                print(f"❌ No access token in response: {tokens}")
                return None
            
            # Get user info
            headers = {'Authorization': f"Bearer {tokens['access_token']}"}
            user_response = requests.get(self.userinfo_url, headers=headers)
            user_response.raise_for_status()
            user_info = user_response.json()
            
            print(f"✅ Successfully got user info: {user_info.get('email')}")
            return user_info
            
        except requests.exceptions.RequestException as e:
            print(f"❌ OAuth token exchange error: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error in token exchange: {str(e)}")
            return None
