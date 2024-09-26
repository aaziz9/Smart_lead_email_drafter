import os
import json

EMAIL_DATA_FOLDER = "./data/Email_data"


def read_email_data(email_address):
    file_path = os.path.join(EMAIL_DATA_FOLDER, f"{email_address}.json")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No email data found for {email_address}")

    with open(file_path, "r") as file:
        email_data = json.load(file)

    return email_data


# Example usage:
if __name__ == "__main__":
    email_address = "ahmed.almansoori@omantel.om"  # Change this as needed
    data = read_email_data(email_address)
    print(json.dumps(data, indent=4))
