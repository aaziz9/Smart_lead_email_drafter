import os
from fastapi import APIRouter

from fastapi import Request
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config

from dotenv import load_dotenv


# Load all the entries from .env file as environment variables
# The .env file should have the values for GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
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
    response = RedirectResponse(url="/outlook_mail")
    try:
        token = await oauth.microsoft.authorize_access_token(request)

        response.set_cookie(
            key="azure_access_token",
            value=token.get('access_token'),
            httponly=True,  # Prevent JavaScript access for security
            samesite="strict"  # Protection against CSRF
        )
    except OAuthError as error:
        return HTMLResponse(f"OAuth Error: {error.error}", status_code=400)

    return response


@azure_auth_router.get(path="/get_azure_auth_token",
                       description="Get the temporary access token if authorization is already done.",
                       tags=["Microsoft Outlook User"])
async def get_token_from_cookie(request: Request):
    token = request.cookies.get("azure_access_token", None)

    if not token:
        return JSONResponse(content={"msg": f"Token not found. Use /azure_login link to login first and then retry."},
                            status_code=401)

    return JSONResponse(content={"azure_access_token": token}, status_code=200)
