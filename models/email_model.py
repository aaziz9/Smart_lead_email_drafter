from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db_utils.database_init import Base


class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, index=True)
    body = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Foreign key to the user who sent the email
    sender_id = Column(Integer, ForeignKey('users.id'))

    # Relationship to the sender
    sender = relationship("User", back_populates="sent_emails")

    # Relationship to recipients (many-to-many through EmailRecipient)
    recipients = relationship("EmailRecipient", back_populates="email")
