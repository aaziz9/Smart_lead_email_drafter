# Smart Lead Email Drafter

## Overview

Smart Lead Email Drafter is a powerful tool designed to streamline the email drafting process for lead key account managers. Using AI models such as Google's Text Bison, this tool assists users in generating professional emails based on given inputs, contexts, and even previous email threads. Whether it's drafting an email from scratch or summarizing and responding to previous conversations, Smart Lead Email Drafter simplifies the workflow for busy professionals.

## Features

- **Email Drafting Based on Context:** The tool can generate emails based on provided input text or previous email threads. It intelligently adapts its responses to fit the context.
- **Custom Actions for Emails:** Users can choose from predefined actions such as "Summarize", "Formal", "Aggressive", "Sad", or "Key Account Manager" to dictate the tone and style of the email.
- **Editable Configuration:** Users can edit parameters like `temperature`, `max_output_tokens`, `topK`, and `topP` in the `app_config.json` file, allowing for control over the AI's creativity and output.
- **Login and Logout with OAuth:** Seamless login and logout functionality using OAuth 2.0 and Google authentication.
- **Save and Load Configuration:** Changes to the AI configuration are saved in a JSON file, making it easy to tweak and persist settings.

## Installation

To get started with Smart Lead Email Drafter, follow these instructions:

1. Clone the repository from GitHub:
   ```bash
   git clone https://github.com/aaziz9/Smart_lead_email_drafter.git
   ```

2. Navigate to the project directory:
   ```bash
   cd Smart_lead_email_drafter
   ```
3. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Set up your environment variables in a .env file. This file should include:
   ```bash
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```
6. Run the application:
   ```bash
   uvicorn main_app:app --reload
   ```

## Configuration

Once logged in, you can edit the configuration parameters for text generation by navigating to the **Edit Configuration** page. You will find the following parameters:

- **Temperature:** Controls the randomness of the output. Lower values make the output more deterministic.
- **Max Output Tokens:** Limits the maximum number of tokens (words or symbols) the model can generate.
- **TopK:** Controls diversity by limiting the number of possible next tokens considered.
- **TopP:** Controls how many top words are considered for text generation. A higher value gives more creative options, while a lower value focuses on the most likely words.

These parameters allow you to fine-tune how the model generates email drafts.

## Usage

- **Login:** Once the application is running, go to `http://localhost:80/login` to authenticate with your Google account.

- **Email Drafting:** After logging in, you can enter your email body in the provided text box, select the action (e.g., "Summarize", "Formal", "Aggressive"), and click **Process**. The tool will generate a draft based on your input.

- **Edit Configuration:** Click on the **Edit Configuration** link in the navbar to modify text generation parameters.

## Deployment

To deploy the application, you can use any cloud provider or containerize it using Docker. For example:

### Build the Docker Image:
```bash
docker build -t smart_lead_email_drafter 
```
### Run the Docker Container:
```bash
docker run -p 80:80 smart_lead_email_drafter
```
## Routes

- `/login`: Redirects to the Google OAuth login page.
- `/logout`: Clears the session and logs the user out.
- `/get_config`: Fetches the current AI configuration.
- `/update_config`: Updates and saves the AI configuration.
- `/context_mail`: Handles context-based email drafting requests.
- `/text_bison`: Handles AI text generation with Google's Text Bison API.
- `/static_files`: Serves static files such as HTML, CSS, and JavaScript.
- `/user`: Handles user-related routes like authentication and session management.

## Future Improvements

Some ideas for future improvements include:

- Expanding the email tone options (e.g., humorous, casual).
- Integration with other AI models for better contextual understanding.
- Multi-language support for non-English emails.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](./LICENSE) file for details.
