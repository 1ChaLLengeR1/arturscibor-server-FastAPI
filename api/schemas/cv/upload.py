from pydantic import BaseModel


class CvUploadPayload(BaseModel):
    file_id: str
