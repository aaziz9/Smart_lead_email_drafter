from fastapi import APIRouter
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from services.text_bison_service import get_processed_text_by_text_bison


gcp_text_bison_router = APIRouter()


@gcp_text_bison_router.post("/get_processed_text")
async def get_processed_text(request: Request):
    """
    Your custom API endpoint to fetch results from GCP for any allowed GCP services
    :param request:
    :return:
    """
    token = request.session.get('token')
    if not token:
        return JSONResponse({"error": "Token not found in session"}, status_code=400)
    else:
        # Read the raw JSON body
        try:
            body: dict = await request.json()  # Parse the incoming request body as JSON
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON body")

        # Process the JSON data as needed
        # Example: Accessing data from the body
        processed_text = get_processed_text_by_text_bison(input_text=body["email_body"],
                                                          action=body["action"],
                                                          auth_token=token["access_token"])["result"]

        return JSONResponse({"response_msg": processed_text}, status_code=200)
