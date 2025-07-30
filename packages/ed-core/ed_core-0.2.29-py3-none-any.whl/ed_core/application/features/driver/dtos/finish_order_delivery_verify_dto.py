from pydantic import BaseModel


class FinishOrderDeliveryVerifyDto(BaseModel):
    otp: str
