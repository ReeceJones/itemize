import asyncio
import itemize.schemas as schemas

from itemize import metadata
from itemize import errors

from itemize.api._deps import CurrentUser, DB

from fastapi import APIRouter, Response
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix='/metadata')

async def append_metadata_list(session: AsyncSession, metadatas: list[schemas.PageMetadata], url: str) -> None:
    if (data := await metadata.get_metadata(session, url)) is not None:
        metadatas.append(data)

@router.post('')
async def get_metadata_for_urls(request: schemas.PageMetadataRequest, _: CurrentUser, session: DB) -> schemas.PageMetadataResponse:
    metadatas = []
    async with asyncio.TaskGroup() as tg:
        for url in request.urls:
            tg.create_task(append_metadata_list(session, metadatas, url))
    return schemas.PageMetadataResponse(metadatas=metadatas)


@router.get('/images/{id}')
async def get_metadata_image(id: int, session: DB) -> Response:
    image = await metadata.get_metadata_image(session, id)
    if image.data is None or image.mime is None:
        raise errors.ImageNotFoundError('Missing data or mime type')
    return Response(content=image.data, media_type=image.mime)
