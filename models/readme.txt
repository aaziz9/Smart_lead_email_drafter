ERD Description:

User
-----
id (PK)
name
email

Email
-----
id (PK)
subject
body
timestamp
sender_id (FK -> User.id)

EmailRecipient
--------------
id (PK)
email_id (FK -> Email.id)
recipient_id (FK -> User.id)
recipient_type (to, cc, bcc)
