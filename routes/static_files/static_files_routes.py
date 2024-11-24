from fastapi import APIRouter
from fastapi.responses import FileResponse

static_files_router = APIRouter()


# Route for index.html
@static_files_router.get("/", include_in_schema=False)
async def email_drafter_page():
    return FileResponse("static/index.html")


# Route for context_mail.html
@static_files_router.get("/context_mail", include_in_schema=False)
async def context_mail():
    return FileResponse("static/context_mail.html")


@static_files_router.get("/config", include_in_schema=False)
async def config_page():
    return FileResponse('static/config.html')


@static_files_router.get("/outlook_mail", include_in_schema=False)
async def outlook_mail_page():
    return FileResponse('static/outlook_mail.html')
