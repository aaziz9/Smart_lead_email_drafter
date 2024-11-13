from bs4 import BeautifulSoup

def encapsulate_thread_email_details_in_response(given_json_response):
    """
    Extracts email threads from the given JSON response and structures them properly.
    :param given_json_response: dict with thread ids and email content.
    :return: A response dict that encapsulates email thread with the related email content.
    """
    messages = given_json_response

    # Group messages by conversationId
    threads_dict = {}
    for email in messages:
        conv_id = email.get('conversationId')
        if not conv_id:
            print("Skipping email due to missing conversationId")
            continue

        if conv_id not in threads_dict:
            threads_dict[conv_id] = {
                "thread_id": conv_id,
                "subject": email.get('subject', 'No Subject Available'),  # Default if no subject is available
                "emails": []
            }

        # Extract uniqueBody content
        unique_body_content = email.get('uniqueBody', {}).get('content', '')

        # Extract and clean the email body content
        if not unique_body_content:
            print(f"Missing body content for email with subject: {email.get('subject', 'No Subject Available')}")
            unique_body_text = "No email content available."
        else:
            try:
                soup = BeautifulSoup(unique_body_content, 'html.parser')
                unique_body_text = soup.get_text(separator=' ', strip=True)
                unique_body_text = ' '.join(unique_body_text.split())
            except Exception as e:
                print(f"Error parsing email content for email with subject '{email.get('subject')}': {e}")
                unique_body_text = "Error processing email content."

        # Prepare the email data dictionary
        email_data = {
            "email_id": email.get('id'),
            "subject": email.get('subject', 'No Subject Available'),
            "body": unique_body_text,
            "timestamp": email.get('receivedDateTime', 'No Timestamp Available'),
            "sender_id": email.get('from', {}).get('emailAddress', {}).get('address', 'Unknown Sender'),
            "recipients": [
                recipient.get('emailAddress', {}).get('address', 'Unknown Recipient')
                for recipient in email.get('toRecipients', [])
            ]
        }

        # Logging missing fields to help debugging
        if email_data["sender_id"] == 'Unknown Sender':
            print(f"Email with ID {email_data['email_id']} is missing sender information.")

        if email_data["subject"] == 'No Subject Available':
            print(f"Email with ID {email_data['email_id']} is missing a subject.")

        threads_dict[conv_id]["emails"].append(email_data)

    # Return all threads as a list
    return list(threads_dict.values())
