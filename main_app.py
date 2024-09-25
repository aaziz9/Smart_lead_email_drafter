from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
import json

from starlette.middleware.sessions import SessionMiddleware
from routes.static_files_routes import static_files_router
from routes.gcp_auth_routes import gcp_router, config
from routes.gcp_text_bison_routes import gcp_text_bison_router
from routes.context_mail_v1_routes import context_mail_router
from db_utils.database_init import Base, engine

app = FastAPI()

# Include routes
app.include_router(static_files_router)
app.include_router(gcp_router)
app.include_router(gcp_text_bison_router)
app.include_router(context_mail_router)

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=config('SECRET_KEY'))

# Mount static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create all tables in the database
Base.metadata.create_all(bind=engine)

# Serve the config.html file, but require login to access it
@app.get("/config")
async def serve_config_page(request: Request):
    if "user" in request.session:  # Check if user is logged in
        return FileResponse('static/config.html')  # Serve the config page
    else:
        return RedirectResponse("/login")  # Redirect to login if not logged in

# Route to get the current config
@app.get("/get_config")
async def get_config():
    try:
        with open('app.config.json', 'r') as config_file:
            config = json.load(config_file)
        return JSONResponse(content=config, status_code=200)
    except FileNotFoundError:
        return JSONResponse(content={"error": "Configuration file not found."}, status_code=500)

# Route to update the config
@app.post("/update_config")
async def update_config(request: Request):
    try:
        body = await request.json()
        new_config = {
            "parameters": {
                "temperature": body.get("temperature"),
                "max_output_tokens": body.get("max_output_tokens"),
                "topK": body.get("topK"),
                "topP": body.get("topP")
            }
        }
        with open('app.config.json', 'w') as config_file:
            json.dump(new_config, config_file, indent=4)
        return JSONResponse(content={"message": "Configuration updated successfully!"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Function to check login status (optional for frontend checks)
@app.get("/login_status")
async def login_status(request: Request):
    if "user" in request.session:
        return JSONResponse(content={"logged_in": True, "user_info": request.session["user"]}, status_code=200)
    else:
        return JSONResponse(content={"logged_in": False}, status_code=401)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
