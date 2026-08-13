from pydantic import BaseModel


class AboutMeImageAttachPayload(BaseModel):
    file_id: str
