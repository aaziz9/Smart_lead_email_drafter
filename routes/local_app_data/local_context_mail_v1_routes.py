import traceback
from fastapi import Request, APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from db_utils.database_init import get_db
from utils.user_utils import get_current_user
from models.user_model import User
from models.email_model import Email
from models.email_thread_model import EmailThread
from models.email_recipient_model import EmailRecipient
from services.google_cloud_platform.gcp_context_mail_service import get_emails_in_curr_thread
from request_schema.email_resource_schema import EmailSchema
from request_schema.email_user_resource_schema import EmailUserSchema

context_mail_router = APIRouter()


# Original GET routes (unchanged)

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


@context_mail_router.get("/context_mail/v2/email_threads", tags=["Context Mail Users"])
async def get_email_threads_for_curr_user(request: Request, db: Session = Depends(get_db),
                                          user_info: dict = Depends(get_current_user)):
    user_email = request.session.get("user_info", {}).get("email")
    if not user_email:
        raise HTTPException(status_code=403, detail="User is not logged in")
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    fetched_email_threads = db.query(EmailThread).join(Email).filter(Email.sender_id == user.id).all()
    return JSONResponse(status_code=200, content={"data": [
        {"id": thread.id, "title": thread.title} for thread in fetched_email_threads
    ]})


@context_mail_router.get("/context_mail/v1/email_threads/{thread_id}/emails", tags=["Context Mail Users"])
async def get_emails_in_thread(thread_id: int, db: Session = Depends(get_db),
                               user_info: dict = Depends(get_current_user)):
    try:
        emails_in_curr_thread = get_emails_in_curr_thread(thread_id=thread_id, db_pointer=db)
        return emails_in_curr_thread
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Unable to get emails from thread")


# New POST Routes for Creating User and Email

@context_mail_router.post("/context_mail/v1/users", tags=["Context Mail Users"])
async def create_user(user: EmailUserSchema, db: Session = Depends(get_db),
                      user_info: dict = Depends(get_current_user)):
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


@context_mail_router.post("/context_mail/v1/emails", tags=["Context Mail Users"])
async def create_email(email_request: EmailSchema, db: Session = Depends(get_db),
                       user_info: dict = Depends(get_current_user)):
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
