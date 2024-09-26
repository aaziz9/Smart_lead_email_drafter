import os
import json
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


# Utility function to read JSON files
def load_json_data(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return {}


if __name__ == "__main__":
    from models import user_model, email_thread_model, email_model, email_recipient_model

    # Path to the directory containing the JSON files
    data_dir = './data/Email_data'

    # Get a list of all JSON files in the directory
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]

    db = SessionLocal()

    try:
        for json_file in json_files:
            # Load data from each JSON file
            email_data = load_json_data(os.path.join(data_dir, json_file))

            # Extract user info from the JSON file name
            user_email = os.path.splitext(json_file)[0]
            user_name = email_data.get("user_name", user_email.split('@')[0])

            # Create or get user
            user = db.query(user_model.User).filter(user_model.User.email == user_email).first()
            if not user:
                user = user_model.User(name=user_name, email=user_email)
                db.add(user)
                db.commit()

            # Add email threads
            for thread in email_data.get("email_threads", []):
                email_thread = db.query(email_thread_model.EmailThread).filter(
                    email_thread_model.EmailThread.title == thread["title"]
                ).first()

                if not email_thread:
                    email_thread = email_thread_model.EmailThread(title=thread["title"])
                    db.add(email_thread)
                    db.commit()

                # Add emails to the thread
                for email_info in thread.get("emails", []):
                    email = email_model.Email(
                        subject=email_info["subject"],
                        body=email_info["body"],
                        sender_id=user.id,  # Use the user id as the sender_id
                        thread_id=email_thread.id
                    )
                    db.add(email)
                    db.commit()

                    # Add recipients to the email
                    for recipient in email_info.get("recipients", []):
                        recipient_user = db.query(user_model.User).filter(user_model.User.email == recipient).first()
                        if not recipient_user:
                            # Create a recipient user if they don't exist
                            recipient_user = user_model.User(name=recipient.split('@')[0], email=recipient)
                            db.add(recipient_user)
                            db.commit()

                        email_recipient = email_recipient_model.EmailRecipient(
                            email_id=email.id,
                            recipient_id=recipient_user.id,
                            recipient_type="to"
                        )
                        db.add(email_recipient)
                    db.commit()

        print("Data loaded from JSON files and inserted into the database successfully!")
    finally:
        # Close the session
        db.close()
