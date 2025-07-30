"""FastAPI routes for Billit Order endpoints."""

from typing import Any, List, Optional

from fastapi import APIRouter, Depends

from ..client import BillitAPIClient

router = APIRouter()


def get_client() -> BillitAPIClient:
    """Return a Billit API client instance."""
    return BillitAPIClient()


@router.get("/orders")
async def list_orders(
    odata_filter: Optional[str] = None,
    skip: int = 0,
    top: int = 120,
    client: BillitAPIClient = Depends(get_client),
) -> dict[str, Any]:
    """Retrieve a list of orders."""
    params = {"$skip": skip, "$top": top}
    if odata_filter:
        params["$filter"] = odata_filter
    return await client.request("GET", "/order", params=params)


@router.post("/orders")
async def create_order(
    order_data: dict[str, Any],
    client: BillitAPIClient = Depends(get_client),
) -> dict[str, Any]:
    """Create a new order."""
    return await client.request("POST", "/order", json=order_data)


@router.get("/orders/deleted")
async def list_deleted_orders(
    client: BillitAPIClient = Depends(get_client),
) -> dict[str, Any]:
    """Retrieve deleted orders for synchronization purposes."""
    return await client.request("GET", "/order/deleted")


@router.get("/orders/{order_id}")
async def get_order(
    order_id: int, client: BillitAPIClient = Depends(get_client)
) -> dict[str, Any]:
    """Retrieve a single order."""
    return await client.request("GET", f"/order/{order_id}")


@router.patch("/orders/{order_id}")
async def update_order(
    order_id: int,
    order_updates: dict[str, Any],
    client: BillitAPIClient = Depends(get_client),
) -> dict[str, Any]:
    """Apply partial updates to an order."""
    return await client.request("PATCH", f"/order/{order_id}", json=order_updates)


@router.delete("/orders/{order_id}")
async def delete_order(
    order_id: int, client: BillitAPIClient = Depends(get_client)
) -> dict[str, Any]:
    """Delete a draft order."""
    return await client.request("DELETE", f"/order/{order_id}")


@router.post("/orders/{order_id}/payments")
async def record_payment(
    order_id: int,
    payment_info: dict[str, Any],
    client: BillitAPIClient = Depends(get_client),
) -> dict[str, Any]:
    """Record a payment for an order."""
    return await client.request("POST", f"/order/{order_id}/payment", json=payment_info)


@router.post("/orders/send")
async def send_order(
    send_data: dict[str, Any],
    client: BillitAPIClient = Depends(get_client),
) -> dict[str, Any]:
    """Send one or more orders via the given transport method."""
    # Extract and validate required fields
    order_ids = send_data.get("order_ids", [])
    transport_type = send_data.get("transport_type", "")
    strict_transport = send_data.get("strict_transport", False)
    
    # Convert to API format
    data = {
        "OrderIDs": order_ids,
        "TransportType": transport_type,
        "StrictTransport": strict_transport,
    }
    return await client.request("POST", "/order/send", json=data)


@router.post("/orders/{order_id}/booking")
async def add_booking_entries(
    order_id: int,
    entries: List[dict[str, Any]],
    client: BillitAPIClient = Depends(get_client),
) -> dict[str, Any]:
    """Attach booking entries to an order."""
    return await client.request("POST", f"/order/{order_id}/booking", json=entries)
