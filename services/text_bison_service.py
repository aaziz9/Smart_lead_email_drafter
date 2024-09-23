import requests

# Base URL for GCP Text Bison model
GCP_TEXT_BISON_MODEL_URL = "https://us-central1-aiplatform.googleapis.com/v1/projects/genz-aismartlead-project/locations/us-central1/publishers/google/models/text-bison:predict"

# Function to process text with different actions using Text Bison
def get_processed_text_by_text_bison(input_text, action, auth_token):
    response_msg = {"status": None, "err_msg": None, "result": None}

    # Define different action prompts, including one for Key Account Manager (KAM)
    action_prompts = {
        "aggressive": f'Rephrase the email content above, based on the following description: "{action}"',
        "polite": f'Rephrase the email content above to make it more polite and customer-friendly.',
        "follow_up": f'Create a follow-up response for the above email content, focusing on maintaining a good client relationship.',
        "clarify_pricing": f'Respond to the above email content, explaining pricing details clearly and professionally.',
        "key_account_manager": (
            f"As a Key Account Manager, your focus is on building long-term relationships, addressing client needs, and providing strategic solutions. "
            f"Rephrase the email content above with the following goals: maintain professionalism, strengthen the relationship, show commitment to the client's success, and offer valuable insights or solutions."
        ),
        # Add more action prompts as needed
    }

    # Choose the appropriate prompt based on the provided action
    action_prompt = action_prompts.get(action, f'Rephrase the email content based on: "{action}"')

    # Create the payload for the GCP Text Bison model request
    payload = {
        "instances": [
            {
                "prompt": "\n".join([input_text, action_prompt])
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
    # Test the function with an example input
    result = get_processed_text_by_text_bison(
        input_text="I wanted to clarify that the name of my team is GenZ and they are working hard to achieve their goals.",
        action="key_account_manager",
        auth_token="ya29.a0AcM612zXHcuKjdHQPsjV6WVNzDkZ1gr6Bk0MzxC0l87yD-AtHNxdH_hkciIYjZ5IWABCqoW5HpH-NToGqOPOpybcghkcIvt1MlUGU78dG71tPzb8mLNW3-358jcKm4qdBAWrx4pA4b9K0D0_sZDtakgSBeIwPgG3jcL0it0GCkWpGxyc9QGwk_J70gBhecEXhxtil1qBbbWQFGBDnqbSMRpXzTEMIyopZgaBPnV8b0dbTg9SOd8jMtIkXxQtp_n9XQ-4qWl0cj8PrMQcRZo17UmsrsH_EqRJmgkvmJGNsTNrA69AR_Kc1xWAGza-iFBgNygxcsJN1VW2sxwluKLHNWn38sMADdg6OqZWOwwBlT5hratqrdU_xli8_45m5qEJq6jk2RWrtnhZM-ZZyu0y1jAd_FCLDUFEWjSLFAaCgYKAV0SARMSFQHGX2MiLimsmqF6L3Hio_1dDQ3kEg0429"
    )
    print(result)
