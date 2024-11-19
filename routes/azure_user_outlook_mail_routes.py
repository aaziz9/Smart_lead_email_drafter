import requests

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import JSONResponse, HTMLResponse

from services.azure_user_outlook_mail_service import transform_response_with_thread_info
from services.azure_user_outlook_mail_service import encapsulate_thread_email_details_in_response

azure_user_outlook_mail_router = APIRouter()


@azure_user_outlook_mail_router.get(path="/azure_user/v1/email_threads/{email_thread_id}",
                                    description="Get Outlook emails of the logged in user (Personal Outlook Account).",
                                    tags=["Microsoft Outlook User"])
async def emails(request: Request, email_thread_id: str):
    access_token = request.cookies.get("azure_access_token", None)

    if not access_token:
        return JSONResponse(content={"msg": f"Token not found. Use /azure_login link to login first and then retry."},
                            status_code=401)

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Prefer': 'outlook.body-content-type="html"'  # Request HTML content
    }

    # https://graph.microsoft.com/v1.0/me/messages?$filter=conversationId eq 'YOUR_CONVERSATION_ID'&$select=id,subject,uniqueBody,receivedDateTime,from,toRecipients
    # thread_id
    messages_endpoint = (
        f"https://graph.microsoft.com/v1.0/me/messages?$filter=conversationId eq '{email_thread_id}'"
        "&$select=id,subject,uniqueBody,receivedDateTime,from,toRecipients"
    )
    msg_response = requests.get(messages_endpoint, headers=headers)
    if msg_response.status_code != 200:
        return HTMLResponse(f"Error fetching messages: {msg_response.text}", status_code=msg_response.status_code)

    # Convert the threads_dict to a list
    list_of_emails_in_thread = encapsulate_thread_email_details_in_response(given_json_response=msg_response.json().get('value', []))
    return JSONResponse(content={"thread_id": email_thread_id,  "emails": list_of_emails_in_thread})


@azure_user_outlook_mail_router.get(path="/azure_user/v1/email_threads",
                                    description="Get Outlook email threads having id and title (subject) "
                                                "Of the logged in user (Personal Outlook Account).",
                                    tags=["Microsoft Outlook User"])
async def email_threads(request: Request):
    access_token = request.cookies.get("azure_access_token", None)

    if not access_token:
        return JSONResponse(content={"msg": f"Token not found. Use /azure_login link to login first and then retry."},
                            status_code=401)

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Prefer': 'outlook.body-content-type="html"'  # Request HTML content
    }

    messages_endpoint = (
        'https://graph.microsoft.com/v1.0/me/messages'
        '?$top=50'
        '&$select=conversationId,subject&$orderby=receivedDateTime desc'
    )
    msg_response = requests.get(messages_endpoint, headers=headers)
    if msg_response.status_code != 200:
        return HTMLResponse(f"Error fetching messages: {msg_response.text}", status_code=msg_response.status_code)

    # Convert the threads_dict to a list
    threads = transform_response_with_thread_info(given_json_response=msg_response.json().get('value', []))
    return JSONResponse(content={"data": threads})
