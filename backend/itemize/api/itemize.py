from itemize import itemize
from itemize import schemas

from itemize.api._deps import MatchUsernameSlug

from fastapi import APIRouter, Body, Query

from typing import Annotated

router = APIRouter(prefix='/itemize')


@router.get('/{username}', dependencies=[MatchUsernameSlug])
async def list_itemizes(username: str, query: str | None = None) -> schemas.ListItemizesResponse:
    itemizes = await itemize.list_itemizes(
        username=username,
        query=query
    )
    return schemas.ListItemizesResponse(
        itemizes=itemizes
    )


@router.post('/{username}', dependencies=[MatchUsernameSlug])
async def create_itemize(username: str, req: Annotated[schemas.CreateItemizeRequest, Body()]) -> schemas.CreateItemizeResponse:
    itemize_ = await itemize.create_itemize(
        name=req.name,
        description=req.description,
        username=username
    )

    return schemas.CreateItemizeResponse(
        itemize=itemize_
    )


@router.get('/{username}/{itemize_slug}', dependencies=[MatchUsernameSlug])
async def get_itemize(username: str, itemize_slug: str, query: str | None = None) -> schemas.GetItemizeResponse:
    itemize_ = await itemize.get_itemize(
        username=username,
        slug=itemize_slug,
        query=query
    )
    return schemas.GetItemizeResponse(
        itemize=itemize_
    )


@router.delete('/{username}/{itemize_slug}', dependencies=[MatchUsernameSlug])
async def delete_itemize(username: str, itemize_slug: str) -> None:
    # TODO
    pass


@router.post('/{username}/{itemize_slug}', dependencies=[MatchUsernameSlug])
async def create_link(username: str, itemize_slug: str, req: Annotated[schemas.CreateLinkRequest, Body()]) -> schemas.CreateLinkResponse:
    link = await itemize.create_link(
        username=username,
        slug=itemize_slug,
        url=req.url
    )

    return schemas.CreateLinkResponse(
        link=link
    )


@router.delete('/{username}/{itemize_slug}/{link_id}', dependencies=[MatchUsernameSlug])
async def delete_link(username: str, itemize_slug: str, link_id: int) -> None:
    await itemize.delete_link(
        username=username,
        slug=itemize_slug,
        link_id=link_id
    )
