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
    from models import user_model, email_thread_model, email_model, email_recipient_model

    # TODO: Correct DATABASE_URL path in case this function is called
    db = SessionLocal()

    try:
        # Insert dummy users
        user1 = user_model.User(name="Ahmed", email="ahmed.almansoori@omantel.om")
        user2 = user_model.User(name="Basma", email="basama.saadi@omantel.om")
        user3 = user_model.User(name="Maryam", email="maryam.almamari@oreedo.com")
        user4 = user_model.User(name="Ali", email="ali.aziz@oreedo.com")
        user5 = user_model.User(name="Zainab", email="zainab.almajali@omantel.com")
        user6 = user_model.User(name="Mohammad", email="mohammad.alawati@oreedo.com")

        db.add_all([user1, user2, user3, user4, user5, user6])
        db.commit()

        email_thread = email_thread_model.EmailThread(title="Partnership Opportunities with Omantel")
        db.add(email_thread)
        db.commit()

        # Insert dummy emails
        email1 = email_model.Email(subject="Partnership Opportunities with Omantel",
                                   body=
                                   """ 
                                   Dear Maryam,
                                    
                                   I hope this message finds you well. My name is Ahmed Al-Mansoori, and I am the Key Account Manager at Omantel. I wanted to reach out to discuss how we can further enhance our partnership and support your business needs.
                                   Last quarter, we saw a significant increase in service adoption, with a 25% growth in our customer base and a 15% increase in sales for our premium packages. I believe there are more opportunities we can explore together.
                                   Could we schedule a time to discuss this further? I look forward to hearing from you.
                                   
                                   Best regards,
                                   Ahmed Al-Mansoori
                                   Key Account Manager, Omantel
                                   +968 1234 5678
                                   ahmed.almansoori@omantel.om
                                   """,
                                   sender_id=1,
                                   thread_id=1)
        email2 = email_model.Email(subject="Re: Partnership Opportunities with Omantel",
                                   body="""
                                   Dear Ahmed,
                                   Thank you for reaching out. I appreciate your interest in enhancing our partnership. The growth numbers sound promising! I am available for a call on Tuesday, October 3rd, at 10:00 AM if that works for you.
                                   Looking forward to our discussion.
                                   
                                   Best,
                                   Maryam Al-Mamari
                                   Operations Manager
                                   Tech Solutions Inc.
                                   """,
                                   sender_id=3,
                                   thread_id=1)
        email3 = email_model.Email(subject="Re: Partnership Opportunities with Omantel",
                                   body=
                                   """
                                   Dear Maryam,
                                   Thank you for your prompt response! I am pleased to confirm our meeting on Tuesday, October 3rd, at 10:00 AM. I will send a calendar invite shortly.
                                   In preparation for our discussion, I will have some detailed sales reports showing how our recent initiatives contributed to a 10% revenue increase. Please let me know if there are specific areas you would like to focus on.
                                   
                                   Best regards,
                                   Ahmed Al-Mansoori
                                   Key Account Manager, Omantel
                                   """,
                                   sender_id=1,
                                   thread_id=1)
        email4 = email_model.Email(subject="Re: Partnership Opportunities with Omantel",
                                   body="""
                                   Dear Ahmed,
                                   
                                   Thank you for confirming the meeting. I would like to focus on the following points during our call:
                                   
                                   1. Current service performance metrics
                                   2. New solutions we could explore, especially those that contributed to the recent sales growth
                                   3. Support for upcoming projects, including projected sales targets
                                   
                                   Looking forward to our conversation!
                                   
                                   Best,
                                   Maryam Al-Mamari
                                   """,
                                   sender_id=3,
                                   thread_id=1)
        email5 = email_model.Email(subject="Follow-Up on Our Recent Discussion",
                                   body="""
                                   Dear Maryam,
                                   
                                   Thank you for the insightful discussion we had on October 3rd. I appreciate your feedback and suggestions. I will compile a detailed proposal addressing the points we discussed, particularly how we can achieve our shared sales targets of 20% growth over the next quarter, and send it over by next Friday.
                                   If you have any additional thoughts in the meantime, please feel free to share.
                                   
                                   Best regards,
                                   Ahmed Al-Mansoori
                                   Key Account Manager, Omantel
                                   """,
                                   sender_id=1,
                                   thread_id=1)

        db.add_all([email1, email2, email3, email4, email5])
        db.commit()

        # Add recipients to the emails
        recipient1 = email_recipient_model.EmailRecipient(email_id=1, recipient_id=3, recipient_type="to")
        recipient2 = email_recipient_model.EmailRecipient(email_id=2, recipient_id=1, recipient_type="to")
        recipient3 = email_recipient_model.EmailRecipient(email_id=3, recipient_id=3, recipient_type="to")
        recipient4 = email_recipient_model.EmailRecipient(email_id=4, recipient_id=1, recipient_type="to")
        recipient5 = email_recipient_model.EmailRecipient(email_id=5, recipient_id=3, recipient_type="to")

        db.add_all([recipient1, recipient2, recipient3, recipient4, recipient5])
        db.commit()

        print("Dummy data inserted successfully!")
    finally:
        # Close the session
        db.close()
