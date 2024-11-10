import requests

from utils.logging_utils import logger_instance


def process_and_add_emails_content_to_response(given_json_response, request_headers):
    """
    Uses the email thread IDs to send request to Gmail and fetch the emails associated with the threads.
    Once all the data is fetched, it is returned as a dict.
    :param given_json_response: dict with thread ids
    :param request_headers: header to use for the upcoming requests to be made to gmail to fetch emails in threads.
    :return: A response dict
    """
    # Parse the thread list
    threads = given_json_response.get('threads', [])
    thread_data = []

    # Fetch details for each thread
    for thread in threads:
        thread_id = thread.get("id")
        thread_detail_url = f"https://www.googleapis.com/gmail/v1/users/me/threads/{thread_id}"

        try:
            thread_detail_response = requests.get(thread_detail_url, headers=request_headers)

            if thread_detail_response.status_code == 200:
                thread_detail = thread_detail_response.json()
                messages = thread_detail.get("messages", [])
                thread_data.append({
                    "threadId": thread_id,
                    "messages": [
                        {
                            "snippet": msg.get("snippet"),
                            "subject": next(
                                (header['value'] for header in msg['payload']['headers'] if header['name'] == 'Subject'),
                                'No Subject'),
                            "from": next(
                                (header['value'] for header in msg['payload']['headers'] if header['name'] == 'From'),
                                'Unknown Sender'),
                        }
                        for msg in messages
                    ]
                })
        except Exception:
            logger_instance.error(f'Unable to process gmail thread: {thread_detail_url}')

    return thread_data
