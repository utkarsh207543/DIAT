from flask import Flask, redirect, request, session, url_for
import os
from dotenv import load_dotenv
import secrets
from google_auth_oauthlib.flow import Flow

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))

# OAuth configuration
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/callback')

@app.route('/')
def index():
    return f'''
    <h1>OAuth Test</h1>
    <p>Client ID: {CLIENT_ID[:10]}...</p>
    <p>Client Secret: {'Set' if CLIENT_SECRET else 'Not set'}</p>
    <p>Redirect URI: {REDIRECT_URI}</p>
    <a href="/login">Test Google Login</a>
    '''

@app.route('/login')
def login():
    # Create OAuth flow
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI]
            }
        },
        scopes=['openid', 'email', 'profile'],
        redirect_uri=REDIRECT_URI
    )
    
    # Generate authorization URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    # Store state for later verification
    session['state'] = state
    
    # Redirect to Google's OAuth page
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    # Get authorization code and state
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    
    if error:
        return f'''
        <h1>Error</h1>
        <p>OAuth Error: {error}</p>
        <a href="/">Go back</a>
        '''
    
    if not code or state != session.get('state'):
        return f'''
        <h1>Error</h1>
        <p>Invalid state or missing code</p>
        <a href="/">Go back</a>
        '''
    
    # Create flow again
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI]
            }
        },
        scopes=['openid', 'email', 'profile'],
        redirect_uri=REDIRECT_URI,
        state=state
    )
    
    try:
        # Exchange code for tokens
        flow.fetch_token(code=code)
        
        # Get user info
        credentials = flow.credentials
        
        return f'''
        <h1>Success!</h1>
        <p>Authentication successful!</p>
        <p>Access token: {credentials.token[:10]}...</p>
        <a href="/">Go back</a>
        '''
    except Exception as e:
        return f'''
        <h1>Error</h1>
        <p>Exception: {str(e)}</p>
        <a href="/">Go back</a>
        '''

if __name__ == '__main__':
    print(f"Starting OAuth test server...")
    print(f"Client ID: {CLIENT_ID[:10]}..." if CLIENT_ID else "CLIENT ID NOT SET")
    print(f"Client Secret: {'SET' if CLIENT_SECRET else 'NOT SET'}")
    print(f"Redirect URI: {REDIRECT_URI}")
    app.run(debug=True, port=5000)
