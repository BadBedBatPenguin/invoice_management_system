from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import Base, engine
from routers import invoices
from settings import file_management_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    file_management_settings.xml_files_directory.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="Invoice Management System", lifespan=lifespan)
app.include_router(invoices.router)
