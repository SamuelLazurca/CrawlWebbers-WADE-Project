from typing import Generic, TypeVar, List
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic.generics import GenericModel  

T = TypeVar("T")

class ItemsResponseSchema(GenericModel, Generic[T]):
    items: List[T]

class DatasetSchema(BaseModel):
    id: str
    name: str
    url: str
    info_hash: str
    size_in_bytes: int
    added_date: str
    dataset_type: str
    number_of_files: int
    number_of_downloads: int
    uploaded_by: str
    uploaded_by_url: str