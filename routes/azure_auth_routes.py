import os
import requests
from fastapi import APIRouter

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

azure_auth_router = APIRouter()


# Configuration data
config_data = {
    'MICROSOFT_CLIENT_ID': os.environ.get("MICROSOFT_CLIENT_ID"),
    'MICROSOFT_CLIENT_SECRET': os.environ.get("MICROSOFT_CLIENT_SECRET"),
    'MICROSOFT_TENANT_ID': os.environ.get("MICROSOFT_TENANT_ID", "common")
}

config = Config(environ=config_data)

# Initialize OAuth
oauth = OAuth(config)

oauth.register(
    name='microsoft',
    client_id=config('MICROSOFT_CLIENT_ID'),
    client_secret=config('MICROSOFT_CLIENT_SECRET'),
    server_metadata_url=f'https://login.microsoftonline.com/{config("MICROSOFT_TENANT_ID")}/v2.0/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'User.Read Mail.Read',
    }
)


@azure_auth_router.get("/azure_login", include_in_schema=False)
async def login(request: Request):
    redirect_uri = "http://localhost/azure_auth"
    return await oauth.microsoft.authorize_redirect(request, redirect_uri)


@azure_auth_router.get("/azure_auth", include_in_schema=False)
async def auth(request: Request):
    try:
        token = await oauth.microsoft.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f"OAuth Error: {error.error}", status_code=400)
    request.session['token'] = token
    return RedirectResponse(url='/')





