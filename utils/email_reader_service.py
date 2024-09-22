import imaplib
import time
import email
from email.header import decode_header
import pyttsx3
import os


MAIL_SERVERS = {
    'gmail.com': {'Server': 'imap.gmail.com'},
    'yahoo.com': {'Server': 'imap.mail.yahoo.com'},
    'aol.com': {'Server': 'imap.aol.com'},
    'outlook.com': {'Server': 'imap-mail.outlook.com'},
    'hotmail.com': {'Server': 'imap-mail.outlook.com'}  # Hotmail uses the same server as Outlook
}


def setup_tts():
    tts = pyttsx3.init()
    tts.say(' ')
    tts.runAndWait()
    return tts


def get_login():
    username = "something@outlook.com"
    password = "asdasdasdasdas"
    return username, password


def decode_mime_words(s):
    decoded_words = decode_header(s)
    return ''.join([str(t[0], t[1] or 'utf-8', errors='replace') if isinstance(t[0], bytes) else t[0] for t in decoded_words])


def get_unseen_messages(server):
    server.select('INBOX')
    result, data = server.search(None, 'UNSEEN')
    if result == 'OK' and data[0]:
        return data[0].split()
    else:
        return []


def sanitize_filename(s):
    return "".join(c for c in s if c.isalnum() or c in (' ', '.', '_')).rstrip()


def main():
    print("Please enter your email account details.")
    username, password = get_login()
    while '@' not in username:
        print("Please enter a valid email address.")
        username, password = get_login()

    domain = username.split("@")[1]

    if domain not in MAIL_SERVERS:
        raise NotImplementedError("Support for your email provider has not been implemented yet")

    try:
        imap_server = imaplib.IMAP4_SSL(
            MAIL_SERVERS[domain]["Server"],
            MAIL_SERVERS[domain].get("Port", 993)
        )
        imap_server.login(username, password)
    except imaplib.IMAP4.error as e:
        print(f"Login failed: {e}")
        return

    tts_engine = setup_tts()

    while True:
        try:
            ids = get_unseen_messages(imap_server)
            if ids:
                for email_id in ids:
                    _, data = imap_server.fetch(email_id, '(RFC822)')
                    raw_email = data[0][1]
                    mail = email.message_from_bytes(raw_email)

                    # Decode headers
                    msg_from = decode_mime_words(mail.get('From'))
                    msg_subject = decode_mime_words(mail.get('Subject'))

                    # Get email body
                    email_body = ""
                    for part in mail.walk():
                        if part.get_content_type() == 'text/plain':
                            charset = part.get_content_charset() or 'utf-8'
                            payload = part.get_payload(decode=True)
                            email_body = payload.decode(charset, errors='replace')
                            break  # Only interested in the first text/plain part

                    print("\nNew message received:")
                    print(f"From: {msg_from}")
                    print(f"Subject: {msg_subject}")
                    print(f"Body: {email_body}")

                    # Use TTS to read the message aloud
                    tts_engine.say(f"New message from {msg_from}")
                    tts_engine.say(f"Subject: {msg_subject}")
                    tts_engine.say(email_body)
                    tts_engine.runAndWait()

                    # Mark the email as seen
                    imap_server.store(email_id, '+FLAGS', '\\Seen')

                    # Save the email to a folder
                    # Extract the sender's email address
                    sender_email = email.utils.parseaddr(msg_from)[1]
                    # Sanitize the sender's email to create a valid folder name
                    folder_name = sanitize_filename(sender_email)
                    # Create the folder if it doesn't exist
                    if not os.path.exists(folder_name):
                        os.makedirs(folder_name)
                    # Create a unique filename for the email
                    timestamp = time.strftime("%Y%m%d-%H%M%S")
                    filename = f"{timestamp}-{email_id.decode()}.txt"
                    filepath = os.path.join(folder_name, filename)
                    # Save the email content to the file
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(f"From: {msg_from}\n")
                        f.write(f"Subject: {msg_subject}\n\n")
                        f.write(email_body)
                    print(f"Email saved to {filepath}")

                # Optional: Sleep after processing emails
                time.sleep(1)
            else:
                time.sleep(5)  # Wait before checking again

        except imaplib.IMAP4.abort as e:
            print("Connection to server lost, reconnecting...")
            try:
                imap_server = imaplib.IMAP4_SSL(
                    MAIL_SERVERS[domain]["Server"],
                    MAIL_SERVERS[domain].get("Port", 993)
                )
                imap_server.login(username, password)
            except Exception as e:
                print(f"Failed to reconnect: {e}")
                break  # Exit the loop
        except Exception as e:
            print(f"An error occurred: {e}")
            break  # Exit the loop


if __name__ == "__main__":
    main()
