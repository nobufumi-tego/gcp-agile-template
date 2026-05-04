"""profile モジュールの Pydantic モデル。"""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class DisplayNameUpdate(BaseModel):
    """PUT /api/v1/profile のリクエストボディ。"""

    display_name: str = Field(min_length=1, max_length=50)

    @field_validator("display_name")
    @classmethod
    def _strip_and_validate(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("display_name は空白のみは不可")
        return stripped
