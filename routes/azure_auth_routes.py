import os
import requests
import uvicorn
from fastapi import APIRouter
from bs4 import BeautifulSoup  # Import Beautiful Soup
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.middleware.sessions import SessionMiddleware
from starlette.config import Config
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

azure_router = APIRouter()


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

@azure_router.get("/microsoft_login_link")
async def homepage():
    return HTMLResponse('<a href="/login">Login with Microsoft</a>')

@azure_router.get("/azure_login")
async def login(request: Request):
    redirect_uri = "http://localhost/azure_auth"
    return await oauth.microsoft.authorize_redirect(request, redirect_uri)

@azure_router.get("/azure_auth")
async def auth(request: Request):
    try:
        token = await oauth.microsoft.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f"OAuth Error: {error.error}", status_code=400)
    request.session['token'] = token
    print(f">>>>>>>>>>>>>> Token Object: {token}")
    return RedirectResponse(url='/azure_emails')


@azure_router.get("/azure_emails")
async def emails(request: Request):
    token = request.session.get('token')
    if not token:
        return RedirectResponse(url='/')
    access_token = token['access_token']
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Prefer': 'outlook.body-content-type="html"'  # Request HTML content
    }

    # Fetch messages
    messages_endpoint = (
        'https://graph.microsoft.com/v1.0/me/messages'
        '?$top=50'
        '&$select=id,subject,uniqueBody,receivedDateTime,from,toRecipients,conversationId'
    )
    msg_response = requests.get(messages_endpoint, headers=headers)
    if msg_response.status_code != 200:
        return HTMLResponse(f"Error fetching messages: {msg_response.text}", status_code=msg_response.status_code)
    messages = msg_response.json().get('value', [])

    # Group messages by conversationId
    threads_dict = {}
    for email in messages:
        conv_id = email.get('conversationId')
        if not conv_id:
            continue  # Skip if conversationId is not available

        if conv_id not in threads_dict:
            threads_dict[conv_id] = {
                "thread_id": conv_id,
                "subject": email.get('subject'),  # Use the subject of the first email as the thread subject
                "emails": []
            }

        # Get the uniqueBody content
        unique_body_content = email.get('uniqueBody', {}).get('content', '')

        # Clean up the body content using Beautiful Soup
        if unique_body_content:
            soup = BeautifulSoup(unique_body_content, 'html.parser')
            # Extract text from the HTML
            unique_body_text = soup.get_text(separator=' ', strip=True)
            # Remove extra spaces
            unique_body_text = ' '.join(unique_body_text.split())
        else:
            unique_body_text = ''

        email_data = {
            "email_id": email.get('id'),
            "subject": email.get('subject'),
            "body": unique_body_text,
            "timestamp": email.get('receivedDateTime'),
            "sender_id": email.get('from', {}).get('emailAddress', {}).get('address'),
            "recipients": [
                recipient.get('emailAddress', {}).get('address')
                for recipient in email.get('toRecipients', [])
            ]
        }
        threads_dict[conv_id]["emails"].append(email_data)

    # Convert the threads_dict to a list
    threads = list(threads_dict.values())

    return JSONResponse(content=threads)


