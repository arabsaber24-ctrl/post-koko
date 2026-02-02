#!/usr/bin/env python3
"""
Get and save YouTube refresh token for permanent authentication
Run this once to get the token, then it will be saved and reused
"""

import os
import json
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

CREDENTIALS_FILE = "client_secrets.json"
TOKEN_FILE = "youtube_token.pickle"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_youtube_token():
    """Get and save YouTube authentication token"""
    credentials = None
    
    # Try to load existing token
    if os.path.exists(TOKEN_FILE):
        print("Loading existing token...")
        with open(TOKEN_FILE, 'rb') as token:
            credentials = pickle.load(token)
            
            # Refresh if expired
            if credentials.expired and credentials.refresh_token:
                print("Token expired, refreshing...")
                credentials.refresh(Request())
                
                # Save refreshed token
                with open(TOKEN_FILE, 'wb') as f:
                    pickle.dump(credentials, f)
                print("✓ Token refreshed and saved")
            else:
                print("✓ Using existing valid token")
            
            return credentials
    
    # Create new token
    print("\n" + "="*70)
    print("YouTube Authorization Required")
    print("="*70)
    print("\nThis will open a browser window for you to authorize the app.")
    print("After authorization, the token will be saved permanently.")
    print("\nAuthorizing...")
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, SCOPES
        )
        
        # Use local server for authorization
        credentials = flow.run_local_server(
            port=8888,
            open_browser=True,
            authorization_prompt_message='Please visit this URL: {url}'
        )
        
        # Save credentials
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(credentials, token)
        
        print("\n" + "="*70)
        print("✅ SUCCESS!")
        print("="*70)
        print("YouTube token has been saved successfully!")
        print("You can now upload videos without manual authorization.")
        print("="*70)
        
        return credentials
        
    except Exception as e:
        print(f"\n✗ Authorization failed: {e}")
        print("\nPlease make sure:")
        print("1. client_secrets.json is in the current directory")
        print("2. You have a browser available")
        print("3. You're using the correct Google account")
        return None

if __name__ == "__main__":
    get_youtube_token()
