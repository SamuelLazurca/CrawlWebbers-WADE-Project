from typing import List, Optional
from fastapi import APIRouter, Query
from app.core.sparql import run_sparql

router = APIRouter()