import requests

# Base URL for GCP Text Bison model
GCP_TEXT_BISON_MODEL_URL = "https://us-central1-aiplatform.googleapis.com/v1/projects/genz-aismartlead-project/locations/us-central1/publishers/google/models/text-bison:predict"


# Function to process text with different actions using Text Bison
def get_processed_text_by_text_bison(input_text, action, auth_token):
    response_msg: dict = {"status": None, "err_msg": None, "result": None}
    action_description = f'Rephrase the content above, and give me an email based on the following description: "{action}"'
    
    # Custom handling for "Omantel Key Account Manager"
    if action == "Omantel Key Account Manager":
        action_description = "Rephrase the email in a formal tone, suitable for an Omantel Key Account Manager. Use telecom industry-specific terms where appropriate."
    elif action == "[CONTEXT_BASED_EMAIL_DRAFTER]":
        action_description = """
        Based on the given emails and keeping all useful facts and figures, generate a summarized draft email including 
        all essential information. This draft will be used as a response to the last email in the given email thread.
        Make sure the responder is the sender of the first email.  
        """

    payload: dict = {
        "instances": [
            {
                "prompt": "\n".join([
                    input_text,
                    action_description
                ])
            }
        ],
        "parameters": {
            "temperature": 0.2,
            "maxOutputTokens": 256,
            "topK": 40,
            "topP": 0.95
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
    result = get_processed_text_by_text_bison(input_text="I wanted to clarify that the name of my team is GenZ and they are trying to work hard to achieve their goals.",
                                              action="aggressive",
                                              auth_token="ya29.a0AcM612zXHcuKjdHQPsjV6WVNzDkZ1gr6Bk0MzxC0l87yD-AtHNxdH_hkciIYjZ5IWABCqoW5HpH-NToGqOPOpybcghkcIvt1MlUGU78dG71tPzb8mLNW3-358jcKm4qdBAWrx4pA4b9K0D0_sZDtakgSBeIwPgG3jcL0it0GCkWpGxyc9QGwk_J70gBhecEXhxtil1qBbbWQFGBDnqbSMRpXzTEMIyopZgaBPnV8b0dbTg9SOd8jMtIkXxQtp_n9XQ-4qWl0cj8PrMQcRZo17UmsrsH_EqRJmgkvmJGNsTNrA69AR_Kc1xWAGza-iFBgNygxcsJN1VW2sxwluKLHNWn38sMADdg6OqZWOwwBlT5hratqrdU_xli8_45m5qEJq6jk2RWrtnhZM-ZZyu0y1jAd_FCLDUFEWjSLFAaCgYKAV0SARMSFQHGX2MiLimsmqF6L3Hio_1dDQ3kEg0429")

    print(result)
