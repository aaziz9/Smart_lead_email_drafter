from fastapi import APIRouter
from fastapi.responses import FileResponse

static_files_router = APIRouter()


@static_files_router.get("/")
async def homepage():
    return FileResponse("static/index.html")
