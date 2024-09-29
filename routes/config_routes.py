import json

from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from utils.user_utils import get_current_user


# Create a router object for the config-related routes
config_routes = APIRouter()


@config_routes.get("/get_config")
async def get_config():
    try:
        with open('./app_config.json', 'r') as config_file:
            config = json.load(config_file)
        return JSONResponse(content=config, status_code=200)
    except FileNotFoundError:
        return JSONResponse(content={"error": "Configuration file not found."}, status_code=500)


@config_routes.post("/update_config")
async def update_config(request: Request, user_info: dict = Depends(get_current_user)):
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
        with open('./app_config.json', 'w') as config_file:
            json.dump(new_config, config_file, indent=4)
        return JSONResponse(content={"message": "Configuration updated successfully!"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
