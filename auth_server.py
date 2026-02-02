
import os
import pickle
from flask import Flask, request
from google_auth_oauthlib.flow import InstalledAppFlow

app = Flask(__name__)

# OAuth2 scope for uploading videos
scopes = ["https://www.googleapis.com/auth/youtube.upload"]
credentials_file = "client_secrets.json"
token_file = "youtube_token.pickle"

# Initialize flow with a placeholder redirect URI
# We will update it once we have the public URL
flow = None

@app.route('/')
def index():
    global flow
    # We need the full URL of this server to set as redirect_uri
    # But since we're using a proxy, we'll just use the manual code entry method
    # which is more reliable in this environment.
    
    # Generate the auth URL
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    
    return f'''
    <h1>YouTube Automation Auth</h1>
    <p>1. <a href="{auth_url}" target="_blank">Click here to authorize</a></p>
    <p>2. After authorizing, you will be redirected to a page that won't load.</p>
    <p>3. Copy the 'code' parameter from that URL and paste it below:</p>
    <form action="/callback" method="get">
        Code: <input type="text" name="code" style="width: 400px;">
        <input type="submit" value="Submit">
    </form>
    '''

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "No code provided."
    
    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials
        with open(token_file, 'wb') as token:
            pickle.dump(credentials, token)
        return "<h1>Success!</h1><p>Authentication successful. You can close this window now. I will proceed with the deployment.</p>"
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>"

if __name__ == "__main__":
    # The user provided redirect_uri is http://localhost, so we must use that in the flow
    flow = InstalledAppFlow.from_client_secrets_file(
        credentials_file, scopes,
        redirect_uri='http://localhost'
    )
    app.run(host='0.0.0.0', port=5000)
