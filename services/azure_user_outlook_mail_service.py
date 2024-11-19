import requests
from bs4 import BeautifulSoup

from utils.logging_utils import logger_instance


def transform_response_with_thread_info(given_json_response):
    """
    Extracts email threads from the given JSON response and structures them properly.
    :param given_json_response: dict with thread ids and email content.
    :return: A response dict that encapsulates email thread with the related email content.
    """
    unique_threads = dict()
    for threadObjDict in given_json_response:
        unique_threads[threadObjDict["conversationId"]] = threadObjDict["subject"]

    return [{"id": thread_id, "title": subject} for thread_id, subject in unique_threads.items()]


def encapsulate_thread_email_details_in_response(given_json_response):
    """
    Extracts email threads from the given JSON response and structures them properly.
    :param given_json_response: dict with thread ids and email content.
    :return: A response dict that encapsulates email thread with the related email content.
    """
    list_of_emails_in_the_thread = list()

    for email in given_json_response:
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

        list_of_emails_in_the_thread.append(email_data)

        # Logging missing fields to help debugging
        if email_data["sender_id"] == 'Unknown Sender':
            logger_instance.warn(f"Email with ID {email_data['email_id']} is missing sender information.")

        if email_data["subject"] == 'No Subject Available':
            logger_instance.warn(f"Email with ID {email_data['email_id']} is missing a subject.")

    return list_of_emails_in_the_thread


def get_emails_in_a_thread_and_transform_response(access_token, email_thread_id):
    transformed_response = []
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Prefer': 'outlook.body-content-type="html"'  # Request HTML content
    }

    messages_endpoint = (
        f"https://graph.microsoft.com/v1.0/me/messages?$filter=conversationId eq '{email_thread_id}'"
        "&$select=id,subject,uniqueBody,receivedDateTime,from,toRecipients"
    )

    msg_response = requests.get(messages_endpoint, headers=headers)
    if msg_response.status_code != 200:
        logger_instance.error(f"Status Code: {msg_response.status_code}, Error fetching messages: {msg_response.text}")
    else:
        transformed_response = encapsulate_thread_email_details_in_response(given_json_response=msg_response.json().get('value', []))

    return transformed_response
