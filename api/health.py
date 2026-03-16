from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/health", summary="Проверка работоспособности")
async def health_check():
    return {"status": "OK"}
