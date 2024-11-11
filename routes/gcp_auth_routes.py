import os
import secrets

import requests
from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse

from authlib.integrations.starlette_client import OAuth
from starlette.config import Config


# Global Declarations
gcp_auth_router = APIRouter()


# Globally used configuration data dictionary
config_data = {
    'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID'),
    'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET'),
    'REDIRECT_URI': 'http://localhost/auth',
    'SECRET_KEY':  secrets.token_hex(32)  # This is for session management
}
config = Config(environ=config_data)


# OAuth setup. Can be used to get an access token from GCP.
# Access token can then be used as an authorization bearer token with requests.
# The request should have an "Authorization" header with "Bearer <access_token_value>" as value.
# This will tell GCP that the user is authorized to access resources within his/her scope.
oauth = OAuth(config)
oauth.register(
    name='google',
    client_id=config('GOOGLE_CLIENT_ID'),
    client_secret=config('GOOGLE_CLIENT_SECRET'),
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    refresh_token_url='https://oauth2.googleapis.com/token',  # Set the refresh token URL
    redirect_uri=config('REDIRECT_URI'),
    client_kwargs={
        'scope': ' '.join(["https://www.googleapis.com/auth/userinfo.profile",
                           "https://www.googleapis.com/auth/userinfo.email",
                           "https://www.googleapis.com/auth/gmail.readonly",
                           "https://www.googleapis.com/auth/generative-language.tuning",
                           "https://www.googleapis.com/auth/generative-language.retriever",
                           "https://www.googleapis.com/auth/cloud-platform"]),
        'access_type': 'offline'},  # Request offline access to get refresh token
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)


@gcp_auth_router.get("/login", include_in_schema=False)
async def login(request: Request):
    """
    :param request: Request object containing data related to the incoming request.
    :return: Redirect to GCP auth page and then GCP tell the browser to redirect to a specific URL
    """
    # Clear the session data
    # request.session.clear()

    # Nonce is used to mitigate any replay attacks where an attacker captures the request and send it later.
    request.session['nonce'] = secrets.token_urlsafe(16)  # Store generated nonce in session for later validation

    return await oauth.google.authorize_redirect(request, config('REDIRECT_URI'), nonce=request.session['nonce'])


@gcp_auth_router.get("/auth", include_in_schema=False)
async def auth(request: Request):
    """
    :param request: The request made by the client (browser) in response to a redirect response made by GCP
    :return: The complete information containing access, id and refresh token.
    """
    # Exchange the authorization code for an access token and refresh token
    token = await oauth.google.authorize_access_token(request)
    nonce = request.session['nonce']

    # Get user information from the ID token
    user = await oauth.google.parse_id_token(token, nonce=nonce)

    # Validate the Nonce
    if nonce != user.get('nonce'):
        return JSONResponse({"error": "Invalid nonce"}, status_code=400)

    # Store the access token in sessions dict for later use
    request.session['gcp_token'] = token
    request.session['user_info'] = {"name": user.name, "email": user.email}

    return RedirectResponse(url="/")


@gcp_auth_router.get("/refresh_token", include_in_schema=False)
async def refresh_token(request: Request):
    """
    When the access token expires, this method can get a new access token.
    :param request: Request object containing data related to the incoming request.
    :return: New access and id token.
    """
    token = request.session.get('gcp_token')
    if not token:
        return JSONResponse({"error": "Token not found in session"}, status_code=400)

    refresh_token_url = 'https://oauth2.googleapis.com/token'
    payload = {
        'client_id': config('GOOGLE_CLIENT_ID'),
        'client_secret': config('GOOGLE_CLIENT_SECRET'),
        'refresh_token': token.get('refresh_token', ''),
        'grant_type': 'refresh_token',
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    response = requests.post(refresh_token_url, data=payload, headers=headers)
    new_token = response.json()

    if 'error' in new_token:
        return JSONResponse({"error": new_token['error']}, status_code=400)

    # Retain the refresh token, so we can keep getting access tokens once they expire.
    new_token['gcp_refresh_token'] = token['refresh_token']

    # Update the existing token info with the new one
    request.session['gcp_token'] = new_token
    return JSONResponse({"new_token": new_token})


@gcp_auth_router.get("/logout", include_in_schema=False)
async def logout(request: Request):
    """
    Logs the user out by clearing the session data.
    :param request: The incoming request object.
    :return: A JSON response confirming the logout.
    """
    # Clear the session data
    request.session.clear()
    return JSONResponse({"message": "Logged out successfully"})


# Check if the user is logged in
@gcp_auth_router.get("/login_status", tags=["User Authorization"])
async def login_status(request: Request):
    token = request.session.get('gcp_token')
    if not token:
        return JSONResponse({"logged_in": False})
    return JSONResponse({"logged_in": True, "user_info": request.session.get('user_info', {})})
