from pydantic import BaseModel


class FinishOrderPickUpVerifyDto(BaseModel):
    otp: str
