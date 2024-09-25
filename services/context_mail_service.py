from fastapi import Depends
from sqlalchemy.orm import Session

from db_utils.database_init import get_db
from models.email_thread_model import EmailThread


def get_emails_in_curr_thread(thread_id: int, db_pointer):
    # Query the thread by its ID
    thread = db_pointer.query(EmailThread).filter(EmailThread.id == thread_id).first()

    if not thread:
        raise Exception("Email thread not found")

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
                "recipients": [curr_recipient.recipient.email for curr_recipient in email.recipients]
            }
            for email in emails_in_thread
        ]
    }
