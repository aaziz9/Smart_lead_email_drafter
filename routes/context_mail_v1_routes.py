from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db_utils.database_init import get_db
from models.user_model import User
from models.email_model import Email
from models.email_thread_model import EmailThread

context_mail_router = APIRouter()


@context_mail_router.get("/context_mail/v1/users")
async def get_users(db: Session = Depends(get_db)):
    fetched_users = db.query(User).all()
    return JSONResponse(status_code=200, content={"data": [user.email for user in fetched_users]})


@context_mail_router.get("/context_mail/v1/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    fetched_user = db.query(User).filter(User.id == user_id).first()
    response_data = {"id": fetched_user.id, "email": fetched_user.email, "name": fetched_user.name} if fetched_user else {}
    return JSONResponse(status_code=200 if fetched_user else 404, content={"data": response_data})


@context_mail_router.get("/context_mail/v1/emails")
async def get_emails(db: Session = Depends(get_db)):
    fetched_emails = db.query(Email).all()
    return JSONResponse(status_code=200,
                        content={"data": [
                            {"id": email.id, "sender_id": email.sender_id, "subject": email.subject, "body": email.body}
                            for email in fetched_emails
                        ]})


@context_mail_router.get("/context_mail/v1/emails/{sender_id}")
async def get_emails_from_a_sender(sender_id: int, db: Session = Depends(get_db)):
    fetched_emails = db.query(Email).filter(Email.sender_id == sender_id).all()
    return JSONResponse(status_code=200, content={"data": [
                            {"id": email.id, "sender_id": email.sender_id, "subject": email.subject, "body": email.body}
                            for email in fetched_emails
                        ]})


@context_mail_router.get("/context_mail/v1/email_threads")
async def get_email_threads(db: Session = Depends(get_db)):
    fetched_email_threads = db.query(EmailThread).all()
    return JSONResponse(
        status_code=200, content={"data": [
            {"id": thread.id, "title": thread.title} for thread in fetched_email_threads
        ]}
    )


@context_mail_router.get("/context_mail/v1/email_threads/{thread_id}/emails")
async def get_emails_in_thread(thread_id: int, db: Session = Depends(get_db)):
    # Query the thread by its ID
    thread = db.query(EmailThread).filter(EmailThread.id == thread_id).first()

    # If thread does not exist, return a 404 error
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    # Query all emails in this thread
    emails_in_thread = thread.emails  # This will automatically query due to the relationship

    # Return the thread details and associated emails in JSON format
    return {
        "thread_id": thread.id,
        "subject": thread.title,
        "emails": [
            {
                "email_id": email.id,
                "subject": email.subject,
                "body": email.body,
                "timestamp": email.timestamp,
                "sender_id": email.sender_id,
            }
            for email in emails_in_thread
        ]
    }
