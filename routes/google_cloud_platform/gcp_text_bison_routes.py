import traceback

from fastapi import APIRouter, Depends
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from services.microsoft_azure.azure_user_outlook_mail_service import get_emails_in_a_thread_and_transform_response
from services.google_cloud_platform.text_bison_service import get_processed_text_by_text_bison
from services.google_cloud_platform.gcp_context_mail_service import get_emails_in_curr_thread
from db_utils.database_init import get_db
from utils.user_utils import get_current_user

gcp_text_bison_router = APIRouter()

# Helper function for logging purposes
def prepare_debug_log_emails_in_thread(emails):
    result_str = ""
    for email in emails:
        result_str += f'Email Subject: {email["subject"]}\n'
        result_str += f'Email Body: {email["body"]}\n'
        result_str += "============ End of email separator ============\n\n"
    return result_str


@gcp_text_bison_router.post("/get_processed_text", tags=["Draft Email"])
async def get_processed_text(request: Request, user_info: dict = Depends(get_current_user)):
    """
    Your custom API endpoint to fetch results from GCP for any allowed GCP services.
    :param user_info: Contains user information fetched from the GCP ID token.
    :param request: Request object received from the client.
    """
    token = request.session.get('gcp_token')
    if not token:
        return JSONResponse({"error": "Token not found in session"}, status_code=400)
    else:
        # Read the raw JSON body
        try:
            body: dict = await request.json()  # Parse the incoming request body as JSON
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON body")

        # Process the JSON data as needed
        processed_text = get_processed_text_by_text_bison(input_text=body["email_body"],
                                                          action=body["action"],
                                                          auth_token=token["access_token"],
                                                          user_info=user_info)["result"]

        return JSONResponse({"response_msg": processed_text}, status_code=200)


@gcp_text_bison_router.get("/text_bison/v1/context_generator/{email_thread_id}", tags=["Draft Email"])
async def get_emails_as_str_in_thread_context(request: Request,
                                              email_thread_id: int,
                                              db: Session = Depends(get_db),
                                              user_info: dict = Depends(get_current_user)):
    """
    Your custom API endpoint to fetch results based on a context which is a collection of emails.
    :param email_thread_id: The ID of the email conversation thread.
    :param db: Pointer referring to the Database.
    :param user_info: Contains user information fetched from the GCP ID token.
    :param request: Request object received from the client.
    """
    token = request.session.get('gcp_token')

    try:
        # Fetch emails from the current thread from the database
        emails_in_curr_thread = get_emails_in_curr_thread(thread_id=email_thread_id, db_pointer=db)

        # Prepare a string to represent all the emails in the thread
        result_str = prepare_debug_log_emails_in_thread(emails_in_curr_thread["emails"])

        # Log result for debugging purposes
        print("Prepared input for GCP Bison:", result_str)

        # Call the GCP Bison API to process the emails and generate a draft response
        processed_text = get_processed_text_by_text_bison(input_text=result_str,
                                                          action="[CONTEXT_BASED_EMAIL_DRAFTER]",
                                                          auth_token=token["access_token"],
                                                          user_info=user_info)["result"]

        return JSONResponse({"response_msg": processed_text}, status_code=200)
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Unable to get emails from thread")


@gcp_text_bison_router.get("/text_bison/v1/azure_context_generator/{email_thread_id}", tags=["Draft Email"])
async def get_azure_emails_as_str_in_thread_context(request: Request,
                                                    email_thread_id: str,
                                                    user_info: dict = Depends(get_current_user)):
    """
    Your custom API endpoint to fetch results based on a context which is a collection of emails.
    :param email_thread_id: The ID of the email conversation thread.
    :param user_info: Contains user information fetched from the GCP ID token.
    :param request: Request object received from the client.
    """
    token = request.session.get('gcp_token')
    azure_token = request.cookies.get("azure_access_token", None)

    try:
        # Fetch emails from Azure Outlook using the Azure service
        emails_in_curr_thread = get_emails_in_a_thread_and_transform_response(access_token=azure_token,
                                                                              email_thread_id=email_thread_id)

        # Prepare a string to represent all the emails in the thread
        result_str = prepare_debug_log_emails_in_thread(emails_in_curr_thread)

        # Log result for debugging purposes
        print("Prepared input for GCP Bison:", result_str)

        # Call the GCP Bison API to process the emails and generate a draft response
        processed_text = get_processed_text_by_text_bison(input_text=result_str,
                                                          action="[CONTEXT_BASED_EMAIL_DRAFTER]",
                                                          auth_token=token["access_token"],
                                                          user_info=user_info)["result"]

        return JSONResponse({"response_msg": processed_text}, status_code=200)
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Unable to get emails from thread")
