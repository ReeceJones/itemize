import asyncio
import itemize.schemas as schemas

from itemize.metadata import get_metadata, get_image

from itemize.api._deps import CurrentUser

from fastapi import APIRouter, Response

router = APIRouter(prefix='/metadata')

async def append_metadata_list(metadatas: list[schemas.PageMetadata], url: str) -> None:
    if (data := await get_metadata(url)) is not None:
        metadatas.append(data)

@router.post('')
async def get_metadata_for_urls(request: schemas.PageMetadataRequest, _: CurrentUser) -> schemas.PageMetadataResponse:
    metadatas = []
    async with asyncio.TaskGroup() as tg:
        for url in request.urls:
            tg.create_task(append_metadata_list(metadatas, url))
    return schemas.PageMetadataResponse(metadatas=metadatas)


@router.get('/images/{metadata_id}')
async def get_metadata_image(metadata_id: int) -> Response:
    return Response(content=await get_image(metadata_id), media_type='image/jpeg')
