from pydantic import BaseModel, Field

from api.schemas.common.multi_lang import MultiLangText


class ToolCreatePayload(BaseModel):
    name: MultiLangText
    information: MultiLangText | None = None
    progress: int | None = Field(default=None, ge=0, le=100, description="Poziom umiejętności w %")
    numeric: int | None = Field(default=None, description="Kolejność wyświetlania")
    link: str | None = Field(default=None, max_length=500)
