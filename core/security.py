from fastapi import Header

async def get_current_user_id(x_user_id: str = Header(..., alias="X-User-ID")) -> str:
    return x_user_id

async def get_user_role(x_user_role: str = Header(..., alias="X-User-Role")) -> str:
    return x_user_role

async def get_user_venue_id(x_user_venue_id: int = Header(..., alias="X-User-Venue-ID")) -> int:
    return x_user_venue_id
