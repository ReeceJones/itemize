from itemize import util
from itemize import schemas
from itemize import models
from itemize import metadata

from itemize.db import DB
from itemize.config import CONFIG
from itemize.errors import ItemizeExistsError, ItemizeNotFoundError, ItemizeLinkNotFoundError, MetadataUnprocessableError, UserNotFoundError

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload


async def create_itemize(name: str, description: str | None, username: str) -> None:
    slug = util.slugify(name)
    async with DB.async_session() as session:
        existing_slug = await session.scalar(
            select(
                func.count()
            )
            .select_from(select(models.Itemize).subquery())
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

        return schemas.Itemize(
            name=itemize.name,
            slug=itemize.slug,
            description=itemize.description,
            owner=itemize.user.username,
            links=[]
        )
    

async def list_itemizes(username: str, *, query: str | None = None) -> list[schemas.Itemize]:
    async with DB.async_session() as session:
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
            schemas.Itemize(
                name=itemize.name,
                slug=itemize.slug,
                description=itemize.description,
                owner=itemize.user.username,
                links=[
                    schemas.Link(
                        id=link.id,
                        url=link.url,
                        page_metadata=schemas.PageMetadata(
                            url=link.page_metadata.url,
                            image_url=link.page_metadata.image_url,
                            title=link.page_metadata.title,
                            description=link.page_metadata.description,
                            site_name=link.page_metadata.site_name,
                        )
                    )
                    for link in itemize.links
                ]
            )
            for itemize in itemizes
            if  query is None or (
                query in itemize.name.lower()
                or query in itemize.description.lower()
                or query in itemize.user.username.lower()
            )
        ]


async def get_itemize(username: str, slug: str, *, query: str | None = None) -> schemas.Itemize:
    async with DB.async_session() as session:
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
                selectinload(models.Itemize.links).selectinload(models.Link.page_metadata).selectinload(models.PageMetadata.images),
                selectinload(models.Itemize.user)
            )
        )
        if itemize is None:
            raise ItemizeNotFoundError('Itemize not found!')
        
        return schemas.Itemize(
            name=itemize.name,
            slug=itemize.slug,
            description=itemize.description,
            owner=itemize.user.username,
            links=[
                schemas.Link(
                    id=link.id,
                    url=link.url,
                    page_metadata=schemas.PageMetadata(
                        url=link.page_metadata.url,
                        image_url=link.page_metadata.image_url if link.page_metadata.image_url != '' else (
                            f'{CONFIG.SERVER_URL}/metadata/images/{link.page_metadata.id}' if len(link.page_metadata.images) > 0 else ''
                        ),
                        title=link.page_metadata.title,
                        description=link.page_metadata.description,
                        site_name=link.page_metadata.site_name,
                    )
                )
                for link in itemize.links
                if query is None or (
                    query in link.page_metadata.title.lower()
                    or query in link.page_metadata.description.lower()
                    or query in link.page_metadata.site_name.lower()
                    or query in link.page_metadata.url.lower()
                )
            ]
        )


async def create_link(username: str, slug: str, url: str) -> schemas.Link:
    metadata_ = await metadata.get_metadata(url)
    if metadata_ is None:
        raise MetadataUnprocessableError('Could not get metadata for url!')
    async with DB.async_session() as session:
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
        
        return schemas.Link(
            id=link.id,
            url=link.url,
            page_metadata=schemas.PageMetadata(
                url=metadata_.url,
                image_url=metadata_.image_url,
                title=metadata_.title,
                description=metadata_.description,
                site_name=metadata_.site_name,
            )
        )


async def delete_link(username: str, slug: str, link_id: int) -> None:
    async with DB.async_session() as session:
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