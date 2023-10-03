from itemize import util
from itemize import schemas
from itemize import models
from itemize import metadata

from itemize.errors import ItemizeExistsError, ItemizeNotFoundError, ItemizeLinkNotFoundError, MetadataUnprocessableError, UserNotFoundError

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession


async def create_itemize(session: AsyncSession, name: str, description: str | None, username: str) -> None:
    slug = util.slugify(name)
    existing_slug = await session.scalar(
        select(
            func.count()
        )
        .select_from(models.Itemize)
        .where(
            models.Itemize.slug == slug,
        )
    )
    if existing_slug > 0:
        raise ItemizeExistsError('Itemize with this name already exists!')

    user_id = await session.scalar(
        select(
            models.User.id
        )
        .select_from(select(models.User).subquery())
        .where(
            models.User.username == username,
        )
    )
    if user_id is None:
        raise UserNotFoundError('User not found!')

    itemize = models.Itemize(
        name=name,
        slug=slug,
        description=description,
        user_id=user_id,
    )
    session.add(itemize)
    await session.commit()
    await session.refresh(itemize, ['user'])

    return await itemize.to_schema()
    

async def list_itemizes(session: AsyncSession, username: str, *, query: str | None = None) -> list[schemas.Itemize]:
    itemizes = await session.scalars(
        select(models.Itemize)
        .join(
            models.User
        )
        .where(
            models.User.username == username,
        )
        .options(
            selectinload(models.Itemize.links),
            selectinload(models.Itemize.links).selectinload(models.Link.page_metadata),
            selectinload(models.Itemize.user)
        )
    )
    return [
        await itemize.to_schema()
        for itemize in itemizes
        if  query is None or (
            query in itemize.name.lower()
            or query in (itemize.description or '').lower()
            or (itemize.user is not None and query in (itemize.user.username or '').lower())
        )
    ]


async def get_itemize(session: AsyncSession, username: str, slug: str, *, query: str | None = None) -> schemas.Itemize:
    itemize = await session.scalar(
        select(models.Itemize)
        .join(
            models.User
        )
        .where(
            models.User.username == username,
            models.Itemize.slug == slug,
        )
        .options(
            selectinload(models.Itemize.links),
            selectinload(models.Itemize.links).selectinload(models.Link.page_metadata).selectinload(models.PageMetadata.image),
            selectinload(models.Itemize.user)
        )
    )
    if itemize is None:
        raise ItemizeNotFoundError('Itemize not found!')
    
    return await itemize.to_schema(link_query=query)


async def create_link(session: AsyncSession, username: str, slug: str, url: str) -> schemas.Link:
    metadata_ = await metadata.get_metadata(session, url)
    if metadata_ is None:
        raise MetadataUnprocessableError('Could not get metadata for url!')
    itemize = await session.scalar(
        select(models.Itemize)
        .join(
            models.User
        )
        .where(
            models.User.username == username,
            models.Itemize.slug == slug,
        )
    )
    if itemize is None:
        raise ItemizeNotFoundError('Itemize not found!')
    
    link = models.Link(
        url=url,
        page_metadata_id=metadata_.id,
        itemize_id=itemize.id
    )
    session.add(link)
    await session.commit()
    
    return await link.to_schema()


async def delete_link(session: AsyncSession, username: str, slug: str, link_id: int) -> None:
    link = await session.scalar(
        select(models.Link)
        .join(
            models.Itemize
        )
        .join(
            models.User
        )
        .where(
            models.User.username == username,
            models.Itemize.slug == slug,
            models.Link.id == link_id,
        )
    )
    if link is None:
        raise ItemizeLinkNotFoundError('Link not found!')
    await session.delete(link)
    await session.commit()