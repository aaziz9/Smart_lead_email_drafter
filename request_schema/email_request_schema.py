from typing import List

class UserCreateRequest:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

class EmailCreateRequest:
    def __init__(self, sender_email: str, receiver_emails: List[str], subject: str, body: str):
        self.sender_email = sender_email
        self.receiver_emails = receiver_emails
        self.subject = subject
        self.body = body
