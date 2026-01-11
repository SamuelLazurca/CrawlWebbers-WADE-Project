from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import filter

app = FastAPI(
    title="DaVi API",
    description="AI powered API for semantic search and data retrieval over DaVi knowledge graphs.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(filter.router, prefix="/api/v1/filter", tags=["Filtering"])
