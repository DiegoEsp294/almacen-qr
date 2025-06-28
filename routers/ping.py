from fastapi import APIRouter

router = APIRouter()


@router.get("/", response_model=str)
def ping():
    return "pong"