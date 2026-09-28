from pydantic import BaseModel

class Detection(BaseModel):
    count: int = 0
    image_b64: str = ""