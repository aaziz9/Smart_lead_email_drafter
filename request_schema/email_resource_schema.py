from typing import List
from pydantic import BaseModel


class EmailSchema(BaseModel):
    sender_email: str
    receiver_emails: List[str]
    subject: str
    body: str
