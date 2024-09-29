import requests

from utils.config_utils import load_config


# Base URL for GCP Text Bison model
GCP_TEXT_BISON_MODEL_URL = "https://us-central1-aiplatform.googleapis.com/v1/projects/genz-aismartlead-project/locations/us-central1/publishers/google/models/text-bison:predict"


# Function to process text with different actions using Text Bison
def get_processed_text_by_text_bison(input_text: str, action: str, auth_token: str, user_info: dict):
    """
    Forwards the input along with an action to GCP text bison. Retrieves and processes the response.
    :param input_text: Input received from the user through the UI.
    :param action: A word considered to be tone or selector of a specific prompt.
    :param auth_token: The actual bearer token.
    :param user_info: A dict containing {"name": user.name, "email": user.email}.
    :return: A dict with response data.
    """
    response_msg: dict = {"status": None, "err_msg": None, "result": None}
    config_params = load_config()  # Load configuration from the app_config.json file.

    action_footer = f"""
    The response must be from following sender:
    sender email is: "{user_info.get('email')}" 
    sender name is: "{user_info.get('name')}.
    """
    action_description = f"""
    Rephrase the content above, and give me an email based on the following description: "{action}"
    {action_footer}
    """

    # Custom handling for "Omantel Key Account Manager"
    if action == "Omantel Key Account Manager":
        action_description = f"""
        Rephrase the email in a formal tone, suitable for an Omantel Key Account Manager. 
        Use telecom industry-specific terms where appropriate.
        {action_footer}
        """
    elif action == "[CONTEXT_BASED_EMAIL_DRAFTER]":
        action_description = f"""
        Based on the given emails and keeping all useful facts and figures, generate a summarized draft email including 
        all essential information. This draft will be used as a response to the last email in the given email thread.
        {action_footer}
        """
    elif action == "[HIJACK]":
        action_description = f"""
        Just for information, my name is {user_info.get('name')}.
        """

    # Prepare payload using parameters loaded from config
    payload: dict = {
        "instances": [
            {
                "prompt": "\n".join([input_text, action_description])
            }
        ],
        "parameters": {
            "temperature": config_params['temperature'],  # Use config params
            "maxOutputTokens": config_params['max_output_tokens'],  # Use config params
            "topK": config_params['topK'],  # Use config params
            "topP": config_params['topP']  # Use config params
        }
    }

    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }

    try:
        # Make the request to the GCP Text Bison model
        response = requests.post(url=GCP_TEXT_BISON_MODEL_URL, headers=headers, json=payload)
        response_msg["status"] = response.status_code

        if response.status_code != 200:
            response_msg["err_msg"] = response.text
        else:
            response_dict = response.json()
            response_msg["result"] = " ".join([prediction["content"] for prediction in response_dict["predictions"]])

    except requests.exceptions.RequestException as e:
        response_msg["err_msg"] = f"Request failed: {str(e)}"
        response_msg["status"] = 500

    return response_msg


if __name__ == "__main__":
    result = get_processed_text_by_text_bison(
        input_text="I wanted to clarify that the name of my team is GenZ and they are trying to work hard to achieve their goals.",
        action="aggressive",
        auth_token="your_auth_token_here",
        user_info={"name": "Mr Anonymous", "email": "mr_unknown@omantel.om"}
    )

    print(result)
