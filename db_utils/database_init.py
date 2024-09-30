from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base

# The relative DB path is different when this script is run as the main script
if __name__ == "__main__":
    DATABASE_URL = "sqlite:///../data/sqlite_db.db"
else:
    DATABASE_URL = "sqlite:///./data/sqlite_db.db"  # This path will be used when main app imports this script

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

    db = SessionLocal()

    try:
        # Insert dummy users
        user1 = user_model.User(name="Atyab", email="syed.atyab.hussain@gmail.com")
        user2 = user_model.User(name="Basma", email="basama.saadi@omantel.om")
        user3 = user_model.User(name="Maryam", email="maryam.almamari@oreedo.com")
        user4 = user_model.User(name="Ali", email="ali.aziz@oreedo.com")
        user5 = user_model.User(name="Zainab", email="zainab.almajali@omantel.com")
        user6 = user_model.User(name="Abdulaziz", email="71528@omantel.om")
        user7 = user_model.User(name="Ghaida", email="ghaidaafarsi96@gmail.com")
        user8 = user_model.User(name="Hiba", email="hibaalsarmi55@gmail.com")
        user9 = user_model.User(name="Sughiya", email="hitiee97@gmail.com")
        user10 = user_model.User(name="Lujain", email="71548@omantel.om")

        # **Correction 1:** Add all users to the database
        db.add_all([user1, user2, user3, user4, user5, user6, user7, user8, user9, user10])
        db.commit()

        # Create email threads
        email_thread1 = email_thread_model.EmailThread(title="Partnership Opportunities with Omantel")
        email_thread2 = email_thread_model.EmailThread(title="Exclusive Offer on iPhone 15 for Omantel Partners")
        email_thread3 = email_thread_model.EmailThread(title="New Collaboration Initiative")  # New thread
        email_thread4 = email_thread_model.EmailThread(title="Inquiry about Omantel Services")  # New thread
        email_thread5 = email_thread_model.EmailThread(title="Feedback on Recent Meeting")  # New thread
        email_thread6 = email_thread_model.EmailThread(title="Project Update: New Marketing Campaign")
        email_thread7 = email_thread_model.EmailThread(title="Meeting Schedule Confirmation")
        email_thread8 = email_thread_model.EmailThread(title="Invitation to Annual Tech Conference")
        email_thread9 = email_thread_model.EmailThread(title="Feedback Request on Product Design")
        email_thread10 = email_thread_model.EmailThread(title="Collaboration Opportunity with XYZ Company")
        email_thread11 = email_thread_model.EmailThread(title="Budget Approval for Q4")
        db.add_all([
            email_thread1, email_thread2, email_thread3, email_thread4, email_thread5, email_thread6, email_thread7,
            email_thread8, email_thread9, email_thread10, email_thread11
        ])
        db.commit()

        # Insert dummy emails between **Atyab** and Maryam
        email1 = email_model.Email(subject="Partnership Opportunities with Omantel",
                                   body=
                                   """ 
                                   Dear Maryam,

                                   I hope this message finds you well. My name is Atyab, and I am the Key Account Manager at Omantel. I wanted to reach out to discuss how we can further enhance our partnership and support your business needs.
                                   Last quarter, we saw a significant increase in service adoption, with a 25% growth in our customer base and a 15% increase in sales for our premium packages. I believe there are more opportunities we can explore together.
                                   Could we schedule a time to discuss this further? I look forward to hearing from you.

                                   Best regards,
                                   Syed Atyab Hussain
                                   Key Account Manager, Omantel
                                   +968 1234 5678
                                   syed.atyab.hussain@gmail.com
                                   """,
                                   sender_id=1,
                                   thread_id=1)
        email2 = email_model.Email(subject="Re: Partnership Opportunities with Omantel",
                                   body="""
                                   Dear Atyab,
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
                                   Syed Atyab Hussain
                                   Key Account Manager, Omantel
                                   """,
                                   sender_id=1,
                                   thread_id=1)
        email4 = email_model.Email(subject="Re: Partnership Opportunities with Omantel",
                                   body="""
                                   Dear Atyab,

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
                                   Syed Atyab Hussain
                                   Key Account Manager, Omantel
                                   """,
                                   sender_id=1,
                                   thread_id=1)

        # Insert dummy emails between **Atyab** and Zainab
        email6 = email_model.Email(subject="Exclusive Offer on iPhone 15 for Omantel Partners",
                                   body="""
                                   Dear Zainab,

                                   I hope you're doing well. I'm excited to inform you about an exclusive offer we have on the new iPhone 15 for our valued partners like you. We've secured a limited stock with special pricing that I believe would be beneficial for your team.
                                   Given the high demand, I'd recommend placing orders early to ensure availability. Please let me know if you're interested, and we can discuss the details.

                                   Best regards,
                                   Syed Atyab Hussain
                                   Key Account Manager, Omantel
                                   +968 1234 5678
                                   syed.atyab.hussain@gmail.com
                                   """,
                                   sender_id=1,
                                   thread_id=2)

        email7 = email_model.Email(subject="Re: Exclusive Offer on iPhone 15 for Omantel Partners",
                                   body="""
                                   Dear Atyab,

                                   Thank you for reaching out with this offer. The new iPhone 15 sounds like a great opportunity. Could you please provide more details on the pricing and the quantities available? Also, are there any bundle packages if we purchase in bulk?

                                   Looking forward to your response.

                                   Best regards,
                                   Zainab Al-Majali
                                   Procurement Manager
                                   """,
                                   sender_id=5,
                                   thread_id=2)

        email8 = email_model.Email(subject="Re: Exclusive Offer on iPhone 15 for Omantel Partners",
                                   body="""
                                   Dear Zainab,

                                   Absolutely, I'd be happy to provide more details. We are offering a 15% discount off the retail price for orders above 50 units, and a 20% discount for orders exceeding 100 units. Additionally, we can include accessory bundles at no extra cost for bulk purchases.

                                   I have attached a detailed proposal with all the pricing tiers and package options. Please review it and let me know if you have any questions or if you'd like to proceed with an order.

                                   Best regards,
                                   Syed Atyab Hussain
                                   Key Account Manager, Omantel
                                   """,
                                   sender_id=1,
                                   thread_id=2)

        # Insert dummy emails between Abdulaziz and Basma
        email9 = email_model.Email(subject="New Collaboration Initiative",
                                   body="""
                                   Dear Basma,

                                   I hope this email finds you well. I'm reaching out to discuss a potential collaboration between our departments. I believe combining our resources could lead to a 30% increase in efficiency based on last quarter's performance metrics.

                                   Would you be available to meet next week to explore this idea further?

                                   Best regards,
                                   Abdulaziz Al-Busaidi
                                   Project Manager, Omantel
                                   """,
                                   sender_id=6,
                                   thread_id=3)

        email10 = email_model.Email(subject="Re: New Collaboration Initiative",
                                    body="""
                                    Dear Abdulaziz,

                                    Thank you for your email. Your proposal sounds interesting, and I agree that collaboration could be beneficial. I'm available on Wednesday at 2 PM. Let me know if that works for you.

                                    Best,
                                    Basma Al-Saadi
                                    """,
                                    sender_id=2,
                                    thread_id=3)

        email11 = email_model.Email(subject="Inquiry about Omantel Services",
                                    body="""
                                    Dear Basma,

                                    I'm considering upgrading our team's communication tools and wanted to inquire about the latest Omantel services that could support this initiative. Specifically, I'm interested in solutions that offer enhanced security features.

                                    Could you provide some information on this?

                                    Regards,
                                    Abdulaziz Al-Busaidi
                                    """,
                                    sender_id=6,
                                    thread_id=4)

        email12 = email_model.Email(subject="Re: Inquiry about Omantel Services",
                                    body="""
                                    Dear Abdulaziz,

                                    Certainly! We have recently launched a new suite of services that might fit your needs. I'll send over the details and we can set up a meeting to discuss them further.

                                    Best,
                                    Basma Al-Saadi
                                    """,
                                    sender_id=2,
                                    thread_id=4)

        email13 = email_model.Email(subject="Feedback on Recent Meeting",
                                    body="""
                                    Dear Basma,

                                    I wanted to provide some feedback on our recent meeting. The insights you provided were very helpful, and I believe implementing those strategies could lead to significant improvements.

                                    Let's keep the communication open as we move forward.

                                    Best regards,
                                    Abdulaziz Al-Busaidi
                                    """,
                                    sender_id=6,
                                    thread_id=5)

        email14 = email_model.Email(subject="Re: Feedback on Recent Meeting",
                                    body="""
                                    Dear Abdulaziz,

                                    Thank you for your feedback. I'm glad you found the meeting productive. I look forward to seeing the positive changes we can achieve together.

                                    Best,
                                    Basma Al-Saadi
                                    """,
                                    sender_id=2,
                                    thread_id=5)

        # Emails in email_thread6 between 'Ghaida' and 'Sughiya'
        email15 = email_model.Email(subject="Project Update: New Marketing Campaign",
                                    body="""
                                    Dear Sughiya,

                                    I wanted to give you an update on our new marketing campaign. The initial designs are ready, and I believe they can increase our engagement by 40% based on previous campaigns.

                                    Please find the attached designs and let me know your feedback by end of day tomorrow.

                                    Best regards,
                                    Ghaida
                                    Marketing Manager
                                    """,
                                    sender_id=7,
                                    thread_id=6)
        email16 = email_model.Email(subject="Re: Project Update: New Marketing Campaign",
                                    body="""
                                    Dear Ghaida,

                                    Thank you for the update. The designs look promising. I have a few suggestions that I will send over shortly.

                                    Best,
                                    Sughiya
                                    """,
                                    sender_id=9,
                                    thread_id=6)

        email17 = email_model.Email(subject="Re: Project Update: New Marketing Campaign",
                                    body="""
                                    Dear Sughiya,

                                    Thank you for your prompt feedback. I look forward to your suggestions.

                                    Best regards
                                    Ghaida
                                    """,
                                    sender_id=7,
                                    thread_id=6)

        email18 = email_model.Email(subject="Meeting Schedule Confirmation",
                                    body="""
                                    Dear Sughiya,

                                    This is a reminder for our meeting scheduled on Thursday, October 5th at 2 PM.
                                    We will discuss the Q4 strategies, and your input is crucial.

                                    Please confirm your availability.

                                    Best
                                    Ghaida
                                    """,
                                    sender_id=7,
                                    thread_id=7)

        email19 = email_model.Email(subject="Re: Meeting Schedule Confirmation",
                                    body="""
                                    Dear Ghaida,

                                    I confirm my attendance for the meeting on Thursday.

                                    Best
                                    Sughiya
                                    """,
                                    sender_id=9,
                                    thread_id=7)

        email20 = email_model.Email(subject="Re: Meeting Schedule Confirmation",
                                    body="""
                                    Dear Sughiya,

                                    Thank you for confirming. See you all at the meeting.

                                    Best
                                    Ghaida
                                    """,
                                    sender_id=7,
                                    thread_id=7)

        # Emails in email_thread8 between 'Ghaida' and 'Sughiya'
        email21 = email_model.Email(
            subject="Invitation to Annual Tech Conference",
            body="""
                    Dear Sughiya,

                    You are cordially invited to attend the Annual Tech Conference happening on November 15th. 
                    This is a great opportunity to learn about the latest trends in our industry.

                    Please let me know if you are interested so I can arrange the tickets.

                    Best regards,
                    Ghaida
                    """,
            sender_id=7,
            thread_id=8)
        email22 = email_model.Email(
            subject="Re: Invitation to Annual Tech Conference",
            body="""
                    Dear Ghaida,

                    I would like to attend the conference. Please include me in the arrangements.

                    Best,
                    Sughiya
                    """,
            sender_id=9,
            thread_id=8)

        # Emails in email_thread9 between 'Hiba' and 'Lujain'
        email23 = email_model.Email(
            subject="Feedback Request on Product Design",
            body="""
                    Dear Lujain,

                    We have completed the initial product design for the new application. I believe this design will enhance user experience by 25%.

                    Please review the attached designs and provide your feedback by the end of this week.

                    Best regards,
                    Hiba
                    Product Manager
                    """,
            sender_id=8,
            thread_id=9)
        email24 = email_model.Email(
            subject="Re: Feedback Request on Product Design",
            body="""
                    Dear Hiba,

                    The design looks great. I will provide detailed feedback by Friday.

                    Best,
                    Lujain
                    """,
            sender_id=10,
            thread_id=9)

        # Emails in email_thread10 between 'Hiba' and 'Lujain'
        email25 = email_model.Email(
            subject="Collaboration Opportunity with XYZ Company",
            body="""
                    Dear Lujain,

                    We have an opportunity to collaborate with XYZ Company on a new project that could increase our market share by 15%.

                    I propose we set up a meeting to discuss the potential benefits and challenges.

                    Please let me know your availability.

                    Best regards,
                    Hiba
                    """,
            sender_id=8,
            thread_id=10)
        email26 = email_model.Email(
            subject="Re: Collaboration Opportunity with XYZ Company",
            body="""
                    Dear Hiba,

                    I'm available next Monday for a meeting. Looking forward to discussing this opportunity.

                    Best,
                    Lujain
                    """,
            sender_id=10,
            thread_id=10)

        # Emails in email_thread11 from 'Hiba' to **Ali**
        email27 = email_model.Email(
            subject="Budget Approval for Q4",
            body="""
                    Dear Ali,

                    I am submitting the budget proposal for Q4. We are expecting a 20% increase in expenditures due to the new marketing campaign.

                    Please review and approve at your earliest convenience.

                    Best regards,
                    Hiba
                    """,
            sender_id=8,
            thread_id=11)

        # ********************************************** #

        db.add_all([
            email1, email2, email3, email4, email5, email6, email7, email8,
            email9, email10, email11, email12, email13, email14, email15,
            email16, email17, email18, email19, email20, email21, email22,
            email23, email24, email25, email26, email27
        ])
        db.commit()

        # Add recipients to the emails
        recipient1 = email_recipient_model.EmailRecipient(email_id=1, recipient_id=3, recipient_type="to")
        recipient2 = email_recipient_model.EmailRecipient(email_id=2, recipient_id=1, recipient_type="to")
        recipient3 = email_recipient_model.EmailRecipient(email_id=3, recipient_id=3, recipient_type="to")
        recipient4 = email_recipient_model.EmailRecipient(email_id=4, recipient_id=1, recipient_type="to")
        recipient5 = email_recipient_model.EmailRecipient(email_id=5, recipient_id=3, recipient_type="to")

        recipient6 = email_recipient_model.EmailRecipient(email_id=6, recipient_id=5, recipient_type="to")
        recipient7 = email_recipient_model.EmailRecipient(email_id=7, recipient_id=1, recipient_type="to")
        recipient8 = email_recipient_model.EmailRecipient(email_id=8, recipient_id=5, recipient_type="to")

        recipient9 = email_recipient_model.EmailRecipient(email_id=9, recipient_id=2, recipient_type="to")
        recipient10 = email_recipient_model.EmailRecipient(email_id=10, recipient_id=6, recipient_type="to")
        recipient11 = email_recipient_model.EmailRecipient(email_id=11, recipient_id=2, recipient_type="to")
        recipient12 = email_recipient_model.EmailRecipient(email_id=12, recipient_id=6, recipient_type="to")
        recipient13 = email_recipient_model.EmailRecipient(email_id=13, recipient_id=2, recipient_type="to")
        recipient14 = email_recipient_model.EmailRecipient(email_id=14, recipient_id=6, recipient_type="to")

        # **Correction 2:** Add recipients for emails 15 to 27
        recipient15 = email_recipient_model.EmailRecipient(email_id=15, recipient_id=9, recipient_type="to")
        recipient16 = email_recipient_model.EmailRecipient(email_id=16, recipient_id=7, recipient_type="to")
        recipient17 = email_recipient_model.EmailRecipient(email_id=17, recipient_id=9, recipient_type="to")
        recipient18 = email_recipient_model.EmailRecipient(email_id=18, recipient_id=9, recipient_type="to")
        recipient19 = email_recipient_model.EmailRecipient(email_id=19, recipient_id=7, recipient_type="to")
        recipient20 = email_recipient_model.EmailRecipient(email_id=20, recipient_id=9, recipient_type="to")
        recipient21 = email_recipient_model.EmailRecipient(email_id=21, recipient_id=9, recipient_type="to")
        recipient22 = email_recipient_model.EmailRecipient(email_id=22, recipient_id=7, recipient_type="to")
        recipient23 = email_recipient_model.EmailRecipient(email_id=23, recipient_id=10, recipient_type="to")
        recipient24 = email_recipient_model.EmailRecipient(email_id=24, recipient_id=8, recipient_type="to")
        recipient25 = email_recipient_model.EmailRecipient(email_id=25, recipient_id=10, recipient_type="to")
        recipient26 = email_recipient_model.EmailRecipient(email_id=26, recipient_id=8, recipient_type="to")
        recipient27 = email_recipient_model.EmailRecipient(email_id=27, recipient_id=4,
                                                           recipient_type="to")  # Assigned to Ali

        db.add_all([
            recipient1, recipient2, recipient3, recipient4, recipient5, recipient6, recipient7, recipient8,
            recipient9, recipient10, recipient11, recipient12, recipient13, recipient14,
            recipient15, recipient16, recipient17, recipient18, recipient19, recipient20,
            recipient21, recipient22, recipient23, recipient24, recipient25, recipient26, recipient27
        ])
        db.commit()

        print("Dummy data inserted successfully!")
    finally:
        # Close the session
        db.close()
