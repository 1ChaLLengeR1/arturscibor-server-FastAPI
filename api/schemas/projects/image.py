from pydantic import BaseModel


class ProjectImageAttachPayload(BaseModel):
    file_id: str
