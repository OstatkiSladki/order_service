from collections.abc import AsyncIterator

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session as core_get_db_session
from core.security import require_user_id, require_user_role, require_user_venue_id


class CurrentUser(BaseModel):
  user_id: int
  role: str


class ManagementUser(CurrentUser):
  venue_id: int


async def get_db_session() -> AsyncIterator[AsyncSession]:
  async for session in core_get_db_session():
    yield session


def get_current_user(
  user_id: int = Depends(require_user_id),
  role: str = Depends(require_user_role),
) -> CurrentUser:
  return CurrentUser(user_id=user_id, role=role)


def get_management_user(
  current_user: CurrentUser = Depends(get_current_user),
  venue_id: int = Depends(require_user_venue_id),
) -> ManagementUser:
  return ManagementUser(user_id=current_user.user_id, role=current_user.role, venue_id=venue_id)
