import requests

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse

from services.gcp_user_gmail_service import process_and_add_emails_content_to_response
from utils.user_utils import get_current_user

gcp_user_email_router = APIRouter()


# Route for index.html
@gcp_user_email_router.get(path="/gcp_user/v1/userinfo",
                           description="Get user name and email of currently logged in user.",
                           tags=["Google's User"])
async def get_gcp_user_info(user_info: dict = Depends(get_current_user)):
    return JSONResponse(
        status_code=200, content={"data": user_info}
    )


@gcp_user_email_router.get("/gcp_user/v1/emails", tags=["Google's User"])
async def read_gmail_emails(request: Request, user_info: dict = Depends(get_current_user)):
    access_token = request.session.get('token')["access_token"]

    # Set up headers with the access token
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    # Gmail API URL to list threads (limiting to 5 threads)
    threads_url = "https://www.googleapis.com/gmail/v1/users/me/threads?maxResults=5"

    # Make the request to Gmail API using `requests`
    response = requests.get(threads_url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to retrieve threads")

    # Parse the thread list
    fetched_email_threads = process_and_add_emails_content_to_response(given_json_response=response.json(),
                                                                       request_headers=headers)

    return {"threads": fetched_email_threads}
