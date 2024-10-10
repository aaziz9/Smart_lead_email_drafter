from fastapi import FastAPI, applications
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

from utils.logging_utils import logger_instance

from starlette.middleware.sessions import SessionMiddleware

from routes.static_files_routes import static_files_router
from routes.gcp_auth_routes import gcp_router, config
from routes.gcp_text_bison_routes import gcp_text_bison_router
from routes.gcp_user_routes import gcp_user_router
from routes.context_mail_v1_routes import context_mail_router
from routes.config_routes import config_routes  # Import config routes

from db_utils.database_init import Base, engine

from models import user_model, email_thread_model, email_model, email_recipient_model


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
    title="AI Smart Lead",
    description="Uses GCP Vertex AI (Text Bison) to understand the natural language and give required insights.",
    version="1.0.2"
)


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

# Include the GCP-related routes
app.include_router(gcp_router)

# Include the GCP text bison-related routes
app.include_router(gcp_text_bison_router)

# Include the GCP user related routes
app.include_router(gcp_user_router)

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
    uvicorn.run(app, host="0.0.0.0", port=8080)
