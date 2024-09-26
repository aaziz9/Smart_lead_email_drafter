import traceback

from fastapi import Request, APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db_utils.database_init import get_db
from utils.user_utils import get_current_user
from models.user_model import User
from models.email_model import Email
from models.email_thread_model import EmailThread
from services.context_mail_service import get_emails_in_curr_thread


context_mail_router = APIRouter()


@context_mail_router.get("/context_mail/v1/users")
async def get_users(db: Session = Depends(get_db), user_info: dict = Depends(get_current_user)):
    fetched_users = db.query(User).all()
    return JSONResponse(status_code=200, content={"data": [user.email for user in fetched_users]})


@context_mail_router.get("/context_mail/v1/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db), user_info: dict = Depends(get_current_user)):
    fetched_user = db.query(User).filter(User.id == user_id).first()
    response_data = {"id": fetched_user.id, "email": fetched_user.email, "name": fetched_user.name} if fetched_user else {}
    return JSONResponse(status_code=200 if fetched_user else 404, content={"data": response_data})


@context_mail_router.get("/context_mail/v1/emails")
async def get_emails(db: Session = Depends(get_db), user_info: dict = Depends(get_current_user)):
    fetched_emails = db.query(Email).all()
    return JSONResponse(status_code=200,
                        content={"data": [
                            {"id": email.id, "sender_id": email.sender_id, "subject": email.subject, "body": email.body}
                            for email in fetched_emails
                        ]})


@context_mail_router.get("/context_mail/v1/emails/{sender_id}")
async def get_emails_from_a_sender(sender_id: int, db: Session = Depends(get_db), user_info: dict = Depends(get_current_user)):
    fetched_emails = db.query(Email).filter(Email.sender_id == sender_id).all()
    return JSONResponse(status_code=200, content={"data": [
                            {"id": email.id, "sender_id": email.sender_id, "subject": email.subject, "body": email.body}
                            for email in fetched_emails
                        ]})


@context_mail_router.get("/context_mail/v1/email_threads")
async def get_email_threads(db: Session = Depends(get_db), user_info: dict = Depends(get_current_user)):
    fetched_email_threads = db.query(EmailThread).all()
    return JSONResponse(
        status_code=200, content={"data": [
            {"id": thread.id, "title": thread.title} for thread in fetched_email_threads
        ]}
    )


@context_mail_router.get("/context_mail/v2/email_threads")
async def get_email_threads_for_curr_user(request: Request, db: Session = Depends(get_db), user_info: dict = Depends(get_current_user)):
    # Get the logged-in user's email from the session
    user_email = request.session.get("user_info", {}).get("email")

    # If the email is not found in the session, return a 403 (Forbidden) error
    if not user_email:
        raise HTTPException(status_code=403, detail="User is not logged in")

    # Query the user by email
    user = db.query(User).filter(User.email == user_email).first()

    # If user is not found, raise a 404 error
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Query the threads where the user is the sender of at least one email
    fetched_email_threads = db.query(EmailThread).join(Email).filter(Email.sender_id == user.id).all()

    return JSONResponse(
        status_code=200, content={"data": [
            {"id": thread.id, "title": thread.title} for thread in fetched_email_threads
        ]}
    )


@context_mail_router.get("/context_mail/v1/email_threads/{thread_id}/emails")
async def get_emails_in_thread(thread_id: int, db: Session = Depends(get_db), user_info: dict = Depends(get_current_user)):
    try:
        emails_in_curr_thread = get_emails_in_curr_thread(thread_id=thread_id, db_pointer=db)
        return emails_in_curr_thread  # Return the thread details and associated emails in JSON format
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Unable to get emails from thread")

