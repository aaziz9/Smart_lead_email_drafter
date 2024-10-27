from pydantic import BaseModel


class EmailUserSchema(BaseModel):
    name: str
    email: str
