from bs4 import BeautifulSoup


def encapsulate_thread_email_details_in_response(given_json_response):
    """
    :param given_json_response: dict with thread ids and email content.
    :return: A response dict that encapsulates email thread with the related email content.
    """
    messages = given_json_response

    # Group messages by conversationId
    threads_dict = {}
    for email in messages:
        conv_id = email.get('conversationId')
        if not conv_id:
            continue  # Skip if conversationId is not available

        if conv_id not in threads_dict:
            threads_dict[conv_id] = {
                "thread_id": conv_id,
                "subject": email.get('subject'),  # Use the subject of the first email as the thread subject
                "emails": []
            }

        # Get the uniqueBody content
        unique_body_content = email.get('uniqueBody', {}).get('content', '')

        # Clean up the body content using Beautiful Soup
        if unique_body_content:
            soup = BeautifulSoup(unique_body_content, 'html.parser')
            # Extract text from the HTML
            unique_body_text = soup.get_text(separator=' ', strip=True)
            # Remove extra spaces
            unique_body_text = ' '.join(unique_body_text.split())
        else:
            unique_body_text = ''

        email_data = {
            "email_id": email.get('id'),
            "subject": email.get('subject'),
            "body": unique_body_text,
            "timestamp": email.get('receivedDateTime'),
            "sender_id": email.get('from', {}).get('emailAddress', {}).get('address'),
            "recipients": [
                recipient.get('emailAddress', {}).get('address')
                for recipient in email.get('toRecipients', [])
            ]
        }
        threads_dict[conv_id]["emails"].append(email_data)

    return list(threads_dict.values())
