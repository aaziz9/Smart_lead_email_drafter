from fastapi import Request, HTTPException


def get_current_user(request: Request):
    # Check if the token exists in the session
    token = request.session.get("gcp_token")

    # Raise an exception if the token is missing or invalid
    if not token:
        raise HTTPException(status_code=403, detail="Not authenticated")

    # Return user info (or any other relevant data if needed)
    return request.session.get("user_info")
