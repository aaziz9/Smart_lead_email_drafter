import os
import secrets
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from services.text_bison_service import get_processed_text_by_text_bison

# Load environment variables from .env file
load_dotenv()

# Configuration data for OAuth and session management
config_data = {
    'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID'),
    'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET'),
    'REDIRECT_URI': 'http://localhost/auth',
    'SECRET_KEY': secrets.token_hex(32)  # Secret key for session management
}
config = Config(environ=config_data)

# Initialize FastAPI app
app = FastAPI()

# Add session middleware to manage user sessions
app.add_middleware(SessionMiddleware, secret_key=config('SECRET_KEY'))

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# OAuth setup for Google authentication and GCP
oauth = OAuth(config)
oauth.register(
    name='google',
    client_id=config('GOOGLE_CLIENT_ID'),
    client_secret=config('GOOGLE_CLIENT_SECRET'),
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://oauth2.googleapis.com/token',
    refresh_token_url='https://oauth2.googleapis.com/token',  # To get refresh token
    redirect_uri=config('REDIRECT_URI'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': ' '.join([
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/generative-language.tuning",
            "https://www.googleapis.com/auth/generative-language.retriever",
            "https://www.googleapis.com/auth/cloud-platform"
        ]),
        'access_type': 'offline'  # Request offline access to get refresh token
    }

)

# Serve the homepage
@app.get("/")
async def homepage():
    return FileResponse("static/index.html")

# Handle user login
@app.get("/login")
async def login(request: Request):
    # Clear session data and create a nonce for the login request
    request.session.clear()
    request.session['nonce'] = secrets.token_urlsafe(16)
    return await oauth.google.authorize_redirect(request, config('REDIRECT_URI'), nonce=request.session['nonce'])

# Handle OAuth redirect and authentication
@app.get("/auth")
async def auth(request: Request):
    # Exchange authorization code for access token
    token = await oauth.google.authorize_access_token(request)
    nonce = request.session['nonce']

    # Validate the nonce to prevent replay attacks
    user = await oauth.google.parse_id_token(token, nonce=nonce)
    if nonce != user.get('nonce'):
        return JSONResponse({"error": "Invalid nonce"}, status_code=400)

    # Store user and token information in session
    request.session['token'] = token
    request.session['user'] = user
    return RedirectResponse(url="/")

# Refresh the access token when it expires
@app.get("/refresh_token")
async def refresh_token(request: Request):
    token = request.session.get('token')
    if not token:
        return JSONResponse({"error": "Token not found in session"}, status_code=400)

    # Prepare request payload to get new access token
    refresh_token_url = 'https://oauth2.googleapis.com/token'
    payload = {
        'client_id': config('GOOGLE_CLIENT_ID'),
        'client_secret': config('GOOGLE_CLIENT_SECRET'),
        'refresh_token': token.get('refresh_token', ''),
        'grant_type': 'refresh_token',
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(refresh_token_url, data=payload, headers=headers)
    new_token = response.json()

    # Check for errors in the response
    if 'error' in new_token:
        return JSONResponse({"error": new_token['error']}, status_code=400)

    # Retain the refresh token and update session with new token
    new_token['refresh_token'] = token['refresh_token']
    request.session['token'] = new_token
    return JSONResponse({"new_token": new_token})

# Check if the user is logged in
@app.get("/login_status")
async def login_status(request: Request):
    token = request.session.get('token')
    if not token:
        return JSONResponse({"logged_in": False})
    return JSONResponse({"logged_in": True, "user_info": request.session.get('user', {})})

# Handle user logout
@app.get("/logout")
async def logout(request: Request):
    request.session.clear()  # Clear session data
    return JSONResponse({"message": "Logged out successfully"})

# Endpoint to process email content using Text Bison
@app.post("/get_processed_text")
async def get_processed_text(request: Request):
    token = request.session.get('token')
    if not token:
        return JSONResponse({"error": "Token not found in session"}, status_code=400)

    try:
        # Parse request body and extract email body and action
        body: dict = await request.json()
        email_body = body.get("email_body", "")
        action = body.get("action", "")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    @app.post("/get_processed_text")
    async def get_processed_text(request: Request):
        # Check if the user is logged in by looking for a token in the session
        token = request.session.get('token')
        if not token:
            # Return an error message if the user is not logged in
            return JSONResponse({"error": "You need to be logged in to process an email."}, status_code=401)

        # Proceed with email processing if the user is logged in

    # Use Text Bison service to process email with given action
    processed_text = get_processed_text_by_text_bison(
        input_text=email_body,
        action=action,
        auth_token=token["access_token"]
    )

    # Check for errors in the Text Bison service response
    if processed_text["status"] != 200:
        return JSONResponse({"error": processed_text["err_msg"]}, status_code=processed_text["status"])

    return JSONResponse({"response_msg": processed_text["result"]}, status_code=200)

# Start the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
