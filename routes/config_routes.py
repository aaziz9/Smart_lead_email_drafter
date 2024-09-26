from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, FileResponse
import json

# Create a router object for the config-related routes
config_routes = APIRouter()

# Serve the config.html file, but only if the user is logged in
@config_routes.get("/config")
async def serve_config_page(request: Request):
    if "user" in request.session:  # Check if user is logged in
        return FileResponse('static/config.html')  # Serve the config page
    else:
        return JSONResponse(content={"message": "Unauthorized"}, status_code=401)

# Route to get the current config
@config_routes.get("/get_config")
async def get_config():
    try:
        with open('app.config.json', 'r') as config_file:
            config = json.load(config_file)
        return JSONResponse(content=config, status_code=200)
    except FileNotFoundError:
        return JSONResponse(content={"error": "Configuration file not found."}, status_code=500)

# Route to update the config
@config_routes.post("/update_config")
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
@config_routes.get("/login_status")
async def login_status(request: Request):
    if "user" in request.session:
        return JSONResponse(content={"logged_in": True, "user_info": request.session["user"]}, status_code=200)
    else:
        return JSONResponse(content={"logged_in": False}, status_code=401)
