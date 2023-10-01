import itemize.api.metadata
import itemize.api.users
import itemize.api.itemize

import itemize.errors

from itemize.db import DB

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


"""
FastAPI App
"""
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


"""
FastAPI Routers
"""
app.include_router(itemize.api.metadata.router, tags=["metadata"])
app.include_router(itemize.api.users.router, tags=["users"])
app.include_router(itemize.api.itemize.router, tags=["itemize"])


"""
FastAPI Exception Handlers
"""
app.add_exception_handler(itemize.errors.BaseError, itemize.errors.handle_fastapi_exception)


"""
FastAPI Events
"""
@app.on_event('startup')
async def startup() -> None:
    await DB.init_db()
