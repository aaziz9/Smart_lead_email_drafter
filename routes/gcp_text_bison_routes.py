import traceback

from fastapi import APIRouter, Depends
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from services.text_bison_service import get_processed_text_by_text_bison
from services.context_mail_service import get_emails_in_curr_thread
from db_utils.database_init import get_db


gcp_text_bison_router = APIRouter()


@gcp_text_bison_router.post("/get_processed_text")
async def get_processed_text(request: Request):
    """
    Your custom API endpoint to fetch results from GCP for any allowed GCP services
    :param request:
    :return:
    """
    token = request.session.get('token')
    if not token:
        return JSONResponse({"error": "Token not found in session"}, status_code=400)
    else:
        # Read the raw JSON body
        try:
            body: dict = await request.json()  # Parse the incoming request body as JSON
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON body")

        # Process the JSON data as needed
        # Example: Accessing data from the body
        processed_text = get_processed_text_by_text_bison(input_text=body["email_body"],
                                                          action=body["action"],
                                                          auth_token=token["access_token"])["result"]

        return JSONResponse({"response_msg": processed_text}, status_code=200)


@gcp_text_bison_router.get("/text_bison/v1/context_generator/{email_thread_id}")
async def get_emails_as_str_in_thread_context(request: Request, email_thread_id: int, db: Session = Depends(get_db)):
    token = request.session.get('token')
    if not token:
        return JSONResponse({"error": "Token not found in session"}, status_code=400)
    else:
        try:
            emails_in_curr_thread = get_emails_in_curr_thread(thread_id=email_thread_id, db_pointer=db)

            result_str = ""
            for email in emails_in_curr_thread["emails"]:
                result_str += f'Email Subject: {email["subject"]}\n'
                result_str += f'Email Body: {email["body"]}\n'
                result_str += "============ End of email separator ============\n\n"

            # return result_str

            processed_text = get_processed_text_by_text_bison(input_text=result_str,
                                                              action="[CONTEXT_BASED_EMAIL_DRAFTER]",
                                                              auth_token=token["access_token"])["result"]

            return JSONResponse({"response_msg": processed_text}, status_code=200)
        except Exception:
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Unable to get emails from thread")

