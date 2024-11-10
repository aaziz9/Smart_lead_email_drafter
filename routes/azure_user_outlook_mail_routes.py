import requests

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse

from bs4 import BeautifulSoup

from services.azure_user_outlook_mail_service import encapsulate_thread_email_details_in_response

azure_user_outlook_mail_router = APIRouter()


@azure_user_outlook_mail_router.get(path="/azure_user/v1/emails",
                                    description="Get Outlook emails of the logged in user (Personal Outlook Account).",
                                    tags=["Microsoft Outlook User"])
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

    # Convert the threads_dict to a list
    threads = encapsulate_thread_email_details_in_response(given_json_response=msg_response.json().get('value', []))
    return JSONResponse(content=threads)
