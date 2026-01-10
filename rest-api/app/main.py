from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import filter, trends, compare, layers, graph, datasets

app = FastAPI(
    title="DaVi API",
    description="OWL + SKOS powered API",
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
app.include_router(trends.router, prefix="/api/v1/trends", tags=["Trends"])
app.include_router(compare.router, prefix="/api/v1/compare", tags=["Compare"])
app.include_router(layers.router, prefix="/api/v1/layers", tags=["Layers"])
app.include_router(graph.router, prefix="/api/v1/graph", tags=["Graph"])
app.include_router(datasets.router, prefix="/api/v1/datasets", tags=["Datasets"])
