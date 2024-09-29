from fastapi import APIRouter
from fastapi.responses import FileResponse

static_files_router = APIRouter()


# Route for index.html
@static_files_router.get("/")
async def email_drafter_page():
    return FileResponse("static/index.html")


# Route for context_mail.html
@static_files_router.get("/context_mail")
async def context_mail():
    return FileResponse("static/context_mail.html")


@static_files_router.get("/config")
async def serve_config_page():
    return FileResponse('static/config.html')
