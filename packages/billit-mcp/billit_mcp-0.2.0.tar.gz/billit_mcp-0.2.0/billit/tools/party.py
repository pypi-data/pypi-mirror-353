"""FastAPI routes for Billit Party (contacts) endpoints."""

from typing import Any, Optional

from fastapi import APIRouter, Depends

from ..client import BillitAPIClient
from ..models.party import Party, PartyCreate, PartyUpdate

router = APIRouter()


def get_client() -> BillitAPIClient:
    """Instantiate and return a Billit API client."""

    return BillitAPIClient()


@router.get("/parties")
async def list_parties(client: BillitAPIClient = Depends(get_client)) -> dict[str, Any]:
    """Retrieve a list of parties."""

    return await client.request("GET", "/party")


@router.post("/parties")
async def create_party(
    party: PartyCreate, client: BillitAPIClient = Depends(get_client)
) -> dict[str, Any]:
    """Create a new party."""

    return await client.request("POST", "/party", json=party.model_dump(by_alias=True))


@router.get("/parties/{party_id}")
async def get_party(
    party_id: int, client: BillitAPIClient = Depends(get_client)
) -> dict[str, Any]:
    """Retrieve a single party by ID."""

    return await client.request("GET", f"/party/{party_id}")


@router.patch("/parties/{party_id}")
async def update_party(
    party_id: int, updates: PartyUpdate, client: BillitAPIClient = Depends(get_client)
) -> dict[str, Any]:
    """Apply partial updates to an existing party."""

    return await client.request(
        "PATCH",
        f"/party/{party_id}",
        json=updates.model_dump(exclude_none=True, by_alias=True),
    )
