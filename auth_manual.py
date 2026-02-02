
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

# OAuth2 scope for uploading videos
scopes = ["https://www.googleapis.com/auth/youtube.upload"]
credentials_file = "client_secrets.json"
token_file = "youtube_token.pickle"

def main():
    # Use a fixed redirect URI for manual flow
    # Since it's a desktop app, we can use http://localhost
    flow = InstalledAppFlow.from_client_secrets_file(
        credentials_file, scopes,
        redirect_uri='http://localhost'
    )
    
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    
    print(f"Please visit this URL: {auth_url}")
    print("\nAfter authorizing, you will be redirected to a page that won't load.")
    print("Copy the 'code' parameter from the URL of that page.")
    
    code = input("Enter the authorization code: ").strip()
    
    flow.fetch_token(code=code)
    credentials = flow.credentials
    
    with open(token_file, 'wb') as token:
        pickle.dump(credentials, token)
    print(f"Authentication successful! Token saved to {token_file}")

if __name__ == "__main__":
    main()
