import traceback

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from db_utils.database_init import get_db
from models.email_model import Email
from models.email_thread_model import EmailThread
from models.user_model import User
from models.email_recipient_model import EmailRecipient
from request_schema.email_request_schema import EmailCreateRequest, UserCreateRequest
from utils.user_utils import get_current_user

context_mail_router = APIRouter()


# Existing routes

@context_mail_router.get("/context_mail/v1/users", tags=["Context Mail Users"])
async def get_users(db: Session = Depends(get_db), user_info: dict = Depends(get_current_user)):
    fetched_users = db.query(User).all()
    return JSONResponse(status_code=200, content={"data": [user.email for user in fetched_users]})


@context_mail_router.get("/context_mail/v1/users/{user_id}", tags=["Context Mail Users"])
async def get_user(user_id: int, db: Session = Depends(get_db), user_info: dict = Depends(get_current_user)):
    fetched_user = db.query(User).filter(User.id == user_id).first()
    response_data = {"id": fetched_user.id, "email": fetched_user.email,
                     "name": fetched_user.name} if fetched_user else {}
    return JSONResponse(status_code=200 if fetched_user else 404, content={"data": response_data})


@context_mail_router.get("/context_mail/v1/emails", tags=["Context Mail Users"])
async def get_emails(db: Session = Depends(get_db), user_info: dict = Depends(get_current_user)):
    fetched_emails = db.query(Email).all()
    return JSONResponse(status_code=200, content={"data": [
        {"id": email.id, "sender_id": email.sender_id, "subject": email.subject, "body": email.body}
        for email in fetched_emails
    ]})


@context_mail_router.get("/context_mail/v1/emails/{sender_id}", tags=["Context Mail Users"])
async def get_emails_from_a_sender(sender_id: int, db: Session = Depends(get_db),
                                   user_info: dict = Depends(get_current_user)):
    fetched_emails = db.query(Email).filter(Email.sender_id == sender_id).all()
    return JSONResponse(status_code=200, content={"data": [
        {"id": email.id, "sender_id": email.sender_id, "subject": email.subject, "body": email.body}
        for email in fetched_emails
    ]})


@context_mail_router.get("/context_mail/v1/email_threads", tags=["Context Mail Users"])
async def get_email_threads(db: Session = Depends(get_db), user_info: dict = Depends(get_current_user)):
    fetched_email_threads = db.query(EmailThread).all()
    return JSONResponse(status_code=200, content={"data": [
        {"id": thread.id, "title": thread.title} for thread in fetched_email_threads
    ]})


@context_mail_router.get("/context_mail/v1/email_threads/{thread_id}/emails", tags=["Context Mail Users"])
async def get_emails_in_thread(thread_id: int, db: Session = Depends(get_db),
                               user_info: dict = Depends(get_current_user)):
    emails_in_thread = db.query(Email).filter(Email.thread_id == thread_id).all()
    return JSONResponse(status_code=200, content={"data": [
        {"id": email.id, "sender_id": email.sender_id, "subject": email.subject, "body": email.body}
        for email in emails_in_thread
    ]})


# New routes

# 1. [POST] Create a new user (manually parse request data)
@context_mail_router.post("/context_mail/v1/users", tags=["Context Mail Users"])
async def create_user(request: Request, db: Session = Depends(get_db), user_info: dict = Depends(get_current_user)):
    # Parse incoming JSON data manually
    user_data = await request.json()
    user = UserCreateRequest(**user_data)  # Manually instantiate UserCreateRequest

    # Check if the user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # Create a new user
    new_user = User(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"id": new_user.id, "name": new_user.name, "email": new_user.email}


# 2. [POST] Create a new email (manually parse request data)
@context_mail_router.post("/context_mail/v1/emails", tags=["Context Mail Users"])
async def create_email(request: Request, db: Session = Depends(get_db), user_info: dict = Depends(get_current_user)):
    # Parse incoming JSON data manually
    email_data = await request.json()
    email_request = EmailCreateRequest(**email_data)  # Manually instantiate EmailCreateRequest

    # Step 1: Fetch sender ID using the sender's email address
    sender = db.query(User).filter(User.email == email_request.sender_email).first()
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")

    # Step 2: Create a new thread with the same title as the email subject
    new_thread = EmailThread(title=email_request.subject)
    db.add(new_thread)
    db.commit()
    db.refresh(new_thread)  # Now you have the thread ID

    # Step 3: Create the email with the subject, body, and reference to the thread
    new_email = Email(
        subject=email_request.subject,
        body=email_request.body,
        sender_id=sender.id,
        thread_id=new_thread.id
    )
    db.add(new_email)
    db.commit()
    db.refresh(new_email)

    # Step 4: Fetch IDs of receivers using their email addresses
    for receiver_email in email_request.receiver_emails:
        receiver = db.query(User).filter(User.email == receiver_email).first()
        if not receiver:
            raise HTTPException(status_code=404, detail=f"Receiver {receiver_email} not found")

        # Step 5: Create the email recipient relationship
        recipient_entry = EmailRecipient(
            email_id=new_email.id,
            recipient_id=receiver.id,
            recipient_type="to"  # Assuming recipient_type is 'to'
        )
        db.add(recipient_entry)

    db.commit()

    return {
        "email_id": new_email.id,
        "thread_id": new_thread.id,
        "subject": new_email.subject,
        "body": new_email.body,
        "sender_id": new_email.sender_id,
        "receivers": email_request.receiver_emails
    }



@context_mail_router.get("/context_mail/v2/email_threads", tags=["Context Mail Users"])
async def get_email_threads_for_curr_user(request: Request, db: Session = Depends(get_db),
                                          user_info: dict = Depends(get_current_user)):
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
