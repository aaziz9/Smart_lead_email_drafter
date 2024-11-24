import os
import secrets

from fastapi import FastAPI, applications
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

from starlette.middleware.sessions import SessionMiddleware
from starlette.config import Config

from utils.logging_utils import logger_instance

from routes.static_files.static_files_routes import static_files_router
from routes.configuration.config_routes import config_routes
from routes.local_app_data.local_context_mail_v1_routes import context_mail_router

from routes.google_cloud_platform.gcp_auth_routes import gcp_auth_router
from routes.google_cloud_platform.gcp_text_bison_routes import gcp_text_bison_router
from routes.google_cloud_platform.gcp_user_gmail_routes import gcp_user_email_router

from routes.microsoft_azure.azure_auth_routes import azure_auth_router
from routes.microsoft_azure.azure_user_outlook_mail_routes import azure_user_outlook_mail_router

from db_utils.database_init import Base, engine

from dotenv import load_dotenv


# Load all the entries from .env file as environment variables
# The .env file should have the values for GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
load_dotenv()


# Globally used configuration data dictionary
config_data = {
    'SECRET_KEY':  secrets.token_hex(32),  # This is for session management
    'UVICORN_PORT': os.getenv('UVICORN_PORT', 80)
}

config = Config(environ=config_data)


def swagger_monkey_patch(*args, **kwargs):
    """
    Wrap the function which is generating the HTML for the /docs endpoint and
    overwrite the default values for the swagger js and css.
    """
    return get_swagger_ui_html(
        *args, **kwargs,
        swagger_js_url="/static/js/swagger-ui-bundle.js",
        swagger_css_url="/static/css/swagger-ui.css",
        swagger_favicon_url="/static/images/swagger_favicon.png")


# Monkey patching get_swagger_ui_html due to a swagger UI bug: https://github.com/fastapi/fastapi/issues/1762
# Without this patch, The URL change doesn't take effect.
applications.get_swagger_ui_html = swagger_monkey_patch


app = FastAPI(
    title="AI Smart Lead API",
    description="Uses GCP Vertex AI (Text Bison) to understand the natural language and give required insights.",
    version="1.0.4"
)


# TODO: Identify the allowed origins and only allow those before going live.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,  # Allow cookies and authentication headers
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Add session middleware to manage user sessions
app.add_middleware(SessionMiddleware, secret_key=config('SECRET_KEY'))


# Include the static file routes
app.include_router(static_files_router)

# Include the GCP related routes
app.include_router(gcp_auth_router)
app.include_router(gcp_text_bison_router)  # GCP text bison-related routes
app.include_router(gcp_user_email_router)  # GCP user Gmail related routes

# Include the Azure related routes
app.include_router(azure_auth_router)
app.include_router(azure_user_outlook_mail_router)  # Microsoft Azure User Outlook email related routes

# Add URL mappings related to all context mail page-related routes
app.include_router(context_mail_router)

# Include the config routes for editing configurations
app.include_router(config_routes)

logger_instance.info("Included all URL Mappings")

# Mount the static directory to serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")
logger_instance.info("Initialized static files")

# Create all tables in the database
Base.metadata.create_all(bind=engine)
logger_instance.info("Configured Database Successfully!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(config('UVICORN_PORT')))
