from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db_utils.database_init import Base


class EmailThread(Base):
    __tablename__ = 'threads'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)

    related_thread = relationship("Email", back_populates="thread")
