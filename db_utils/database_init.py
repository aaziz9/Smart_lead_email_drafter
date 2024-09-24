from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./data/sqlite_db.db"

# Create the SQLite database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a session local instance for DB operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

# Metadata object for the engine
metadata = MetaData()


# Dependency to get a new session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    from models import user_model, email_model, email_recipient_model

    # TODO: Correct DATABASE_URL path in case this function is called
    db = SessionLocal()

    try:
        # Insert dummy users
        user1 = user_model.User(name="Alice", email="alice@example.com")
        user2 = user_model.User(name="Bob", email="bob@example.com")
        user3 = user_model.User(name="Charlie", email="charlie@example.com")

        db.add_all([user1, user2, user3])
        db.commit()

        # Insert dummy emails
        email1 = email_model.Email(subject="Meeting Reminder", body="Don't forget the meeting at 10 AM tomorrow.", sender_id=1)
        email2 = email_model.Email(subject="Project Update", body="Here is the latest update on the project.", sender_id=2)

        db.add_all([email1, email2])
        db.commit()

        # Add recipients to the emails
        recipient1 = email_recipient_model.EmailRecipient(email_id=1, recipient_id=2, recipient_type="to")
        recipient2 = email_recipient_model.EmailRecipient(email_id=1, recipient_id=3, recipient_type="cc")
        recipient3 = email_recipient_model.EmailRecipient(email_id=2, recipient_id=1, recipient_type="to")

        db.add_all([recipient1, recipient2, recipient3])
        db.commit()

        print("Dummy data inserted successfully!")
    finally:
        # Close the session
        db.close()