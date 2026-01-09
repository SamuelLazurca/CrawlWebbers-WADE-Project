from fastapi import APIRouter, HTTPException
from app.models.schemas import DatasetSchema, ItemsResponseSchema
from app.services.datasets_service import datasets_get_all_query, dataset_get_by_id_query

router = APIRouter()

@router.get("/")
def get_datasets() -> ItemsResponseSchema[DatasetSchema]:
    items = datasets_get_all_query()
    return ItemsResponseSchema[DatasetSchema](items=items)

@router.get("/{dataset_id}")
def get_dataset_by_id(dataset_id: str) -> DatasetSchema | None:
    dataset = dataset_get_by_id_query(dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset
