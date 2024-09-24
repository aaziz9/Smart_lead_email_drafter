from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db_utils.database_init import get_db
from models.user_model import User
from models.email_model import Email

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

