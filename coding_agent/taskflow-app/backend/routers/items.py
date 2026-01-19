from fastapi import APIRouter
from models.item import Item

router = APIRouter()

@router.get("/")
def get_items():
    return {"items": []}

@router.post("/")
def create_item(item: Item):
    return {"item": item, "id": 1}