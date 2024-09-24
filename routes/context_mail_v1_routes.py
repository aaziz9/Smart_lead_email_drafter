from fastapi import APIRouter
from fastapi.responses import FileResponse

context_mail_router = APIRouter()


@context_mail_router.get("/context_mail/v1/users")
async def get_users():
    return {"users": {}}

