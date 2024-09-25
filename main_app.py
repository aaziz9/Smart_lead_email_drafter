from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from starlette.middleware.sessions import SessionMiddleware

from routes.static_files_routes import static_files_router
from routes.gcp_auth_routes import gcp_router, config
from routes.gcp_text_bison_routes import gcp_text_bison_router
from routes.context_mail_v1_routes import context_mail_router

from db_utils.database_init import Base, engine

from models import user_model, email_thread_model, email_model, email_recipient_model


app = FastAPI()

# Include the static file routes
app.include_router(static_files_router)

# Include the GCP-related routes
app.include_router(gcp_router)

# Include the GCP text bison-related routes
app.include_router(gcp_text_bison_router)

# Add URL mappings related to all context mail page related routes
app.include_router(context_mail_router)

# Add session middleware to manage user sessions
app.add_middleware(SessionMiddleware, secret_key=config('SECRET_KEY'))
# Mount the static directory to serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create all tables in the database
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
