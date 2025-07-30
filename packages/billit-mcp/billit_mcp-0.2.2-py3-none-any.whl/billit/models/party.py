from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Party(BaseModel):
    party_id: int = Field(alias="PartyID")
    name: str = Field(alias="Name")

    model_config = ConfigDict(populate_by_name=True)


class PartyCreate(BaseModel):
    name: str


class PartyUpdate(BaseModel):
    name: Optional[str] = None
