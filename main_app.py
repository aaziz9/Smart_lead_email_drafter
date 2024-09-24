from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routes.static_files_routes import static_files_router
from routes.gcp_auth_routes import gcp_router, config
from routes.gcp_text_bison_routes import gcp_text_bison_router

from starlette.middleware.sessions import SessionMiddleware

from db_utils.database_init import Base, engine


app = FastAPI()

# Add URL mappings from routes. This is done to keep the main_app.py clean and highly cohesive.
app.include_router(static_files_router)

# Add URL mappings related to all gcp related routes
app.include_router(gcp_router)

# Add URL mappings related to all gcp text bison related routes
app.include_router(gcp_text_bison_router)

# Add session middleware to manage user sessions
app.add_middleware(SessionMiddleware, secret_key=config('SECRET_KEY'))

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# Create all tables in the database
Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
