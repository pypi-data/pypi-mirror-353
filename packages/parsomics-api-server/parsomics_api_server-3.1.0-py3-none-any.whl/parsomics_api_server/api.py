from parsomics_api_server.entities.router import router as entities_router
from parsomics_api_server.querying.router import router as querying_router

from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(entities_router)
app.include_router(querying_router)
