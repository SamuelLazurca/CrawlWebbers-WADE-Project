from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import FRONTEND_URL
from app.core.security import get_api_key
from app.routers import filter, trends, compare, layers, graph, datasets
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

app = FastAPI(
    title="DaVi API",
    description="OWL + SKOS powered API",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(filter.router, prefix="/api/v1/filter", tags=["Filtering"], dependencies=[Depends(get_api_key)])
app.include_router(trends.router, prefix="/api/v1/trends", tags=["Trends"], dependencies=[Depends(get_api_key)])
app.include_router(compare.router, prefix="/api/v1/compare", tags=["Compare"], dependencies=[Depends(get_api_key)])
app.include_router(layers.router, prefix="/api/v1/layers", tags=["Layers"], dependencies=[Depends(get_api_key)])
app.include_router(graph.router, prefix="/api/v1/graph", tags=["Graph"], dependencies=[Depends(get_api_key)])
app.include_router(datasets.router, prefix="/api/v1/datasets", tags=["Datasets"], dependencies=[Depends(get_api_key)])

@app.get("/health")
def health():
    return {"status": "ok"}
