from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db_utils.database_init import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

    # Relationship to emails they send
    sent_emails = relationship("Email", back_populates="sender")

    # Relationship to emails they receive (via the recipient table)
    received_emails = relationship("EmailRecipient", back_populates="recipient")
