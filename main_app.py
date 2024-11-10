from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from utils.logging_utils import logger_instance

from starlette.middleware.sessions import SessionMiddleware

from routes.static_files_routes import static_files_router
from routes.config_routes import config_routes
from routes.local_context_mail_v1_routes import context_mail_router

from routes.gcp_auth_routes import gcp_auth_router, config
from routes.gcp_text_bison_routes import gcp_text_bison_router
from routes.gcp_user_gmail_routes import gcp_user_email_router

from routes.azure_auth_routes import azure_auth_router
from routes.azure_user_outlook_mail_routes import azure_user_outlook_mail_router

from db_utils.database_init import Base, engine

from models import user_model, email_thread_model, email_model, email_recipient_model


app = FastAPI()


# TODO: Identify the allowed origins and only allow those before going live.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,  # Allow cookies and authentication headers
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


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

# Add session middleware to manage user sessions
app.add_middleware(SessionMiddleware, secret_key=config('SECRET_KEY'))

# Mount the static directory to serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")
logger_instance.info("Initialized static files")

# Create all tables in the database
Base.metadata.create_all(bind=engine)
logger_instance.info("Configured Database Successfully!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
