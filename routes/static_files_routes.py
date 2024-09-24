from fastapi import APIRouter
from fastapi.responses import FileResponse

static_files_router = APIRouter()


@static_files_router.get("/")
async def email_drafter_page():
    return FileResponse("static/index.html")


@static_files_router.get("/context_mail")
async def context_mail_page():
    return FileResponse("static/context_mail.html")
