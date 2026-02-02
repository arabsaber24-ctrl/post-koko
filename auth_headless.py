
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

# OAuth2 scope for uploading videos
scopes = ["https://www.googleapis.com/auth/youtube.upload"]
credentials_file = "client_secrets.json"
token_file = "youtube_token.pickle"

def main():
    # Force the use of a local server and try to get the authorization URL
    flow = InstalledAppFlow.from_client_secrets_file(
        credentials_file, scopes
    )
    # We'll use run_local_server but we need to catch the URL it generates
    # Since we can't easily intercept the printed output and then open a browser in one step
    # we'll use a more manual approach if possible or just try to use the browser tool.
    
    # Actually, run_local_server with host='localhost' and port=8080 might work if we can open the URL.
    # But wait, the browser tool can open URLs.
    
    print("Please visit the URL printed below to authorize the application.")
    credentials = flow.run_local_server(port=8080, open_browser=False)
    
    with open(token_file, 'wb') as token:
        pickle.dump(credentials, token)
    print(f"Authentication successful! Token saved to {token_file}")

if __name__ == "__main__":
    main()
