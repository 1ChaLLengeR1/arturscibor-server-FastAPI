from pydantic import BaseModel


class WorkLogoAttachPayload(BaseModel):
    file_id: str
