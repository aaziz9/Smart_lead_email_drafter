from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from db_utils.database_init import Base


class EmailRecipient(Base):
    __tablename__ = 'email_recipients'

    id = Column(Integer, primary_key=True, index=True)

    # Foreign key to the email
    email_id = Column(Integer, ForeignKey('emails.id'))

    # Foreign key to the recipient (user)
    recipient_id = Column(Integer, ForeignKey('users.id'))

    # Type of recipient (to, cc, bcc)
    recipient_type = Column(String, default='to')

    # Relationships
    email = relationship("Email", back_populates="recipients")
    recipient = relationship("User", back_populates="received_emails")
