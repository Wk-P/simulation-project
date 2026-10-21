from pydantic import BaseModel


# JWT

class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str