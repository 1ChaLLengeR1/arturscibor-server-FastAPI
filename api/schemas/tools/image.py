from pydantic import BaseModel


class ToolImageAttachPayload(BaseModel):
    file_id: str
