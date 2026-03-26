from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader


x_user_id_header = APIKeyHeader(name="X-User-ID", scheme_name="X-User-ID", auto_error=False)
x_user_role_header = APIKeyHeader(name="X-User-Role", scheme_name="X-User-Role", auto_error=False)
x_user_venue_id_header = APIKeyHeader(
  name="X-User-Venue-ID", scheme_name="X-User-Venue-ID", auto_error=False
)


def require_user_id(x_user_id: str | None = Security(x_user_id_header)) -> int:
  if x_user_id is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-User-ID header is required")
  try:
    return int(x_user_id)
  except ValueError as exc:
    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="X-User-ID must be integer") from exc


def require_user_role(x_user_role: str | None = Security(x_user_role_header)) -> str:
  if x_user_role is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-User-Role header is required")
  return x_user_role


def require_user_venue_id(
  x_user_venue_id: str | None = Security(x_user_venue_id_header),
) -> int:
  if x_user_venue_id is None:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="X-User-Venue-ID header is required",
    )
  try:
    return int(x_user_venue_id)
  except ValueError as exc:
    raise HTTPException(
      status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
      detail="X-User-Venue-ID must be integer",
    ) from exc
