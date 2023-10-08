from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr, relationship
from sqlalchemy.exc import InvalidRequestError

from itemize.config import CONFIG

from itemize import schemas

from datetime import datetime
from typing import Any, Optional


class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    async def to_schema(self) -> schemas.BaseModel:
        return schemas.DBModel(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    async def to_dict(self) -> dict[str, Any]:
        return (await Base.to_schema(self)).model_dump()
    

class MetadataImage(Base):
    mime: Mapped[str | None]
    data: Mapped[bytes | None] = mapped_column(default=None)
    source_image_url: Mapped[str | None] = None

    @property
    def url(self) -> str | None:
        if self.data is None:
            return None
        return f'{CONFIG.SERVER_URL}/metadata/images/{self.id}'

    async def to_schema(self) -> schemas.MetadataImage:
        return schemas.MetadataImage(
            **(await super().to_dict()),
            mime=self.mime,
            source_image_url=self.source_image_url,
            url=self.url,
        )


class PageMetadata(Base):
    url: Mapped[str] = mapped_column(index=True, unique=True)
    image_url: Mapped[str | None]
    title: Mapped[str | None]
    description: Mapped[str | None]
    site_name: Mapped[str | None]
    price: Mapped[str | None]
    currency: Mapped[str | None]

    image_id: Mapped[int | None] = mapped_column(ForeignKey('metadataimage.id'))
    image: Mapped[Optional['MetadataImage']] = relationship('MetadataImage', lazy='raise')

    async def to_schema(self) -> schemas.PageMetadata:
        image = None

        try:
            if self.image is not None:
                image = await self.image.to_schema()
        except InvalidRequestError:
            pass

        return schemas.PageMetadata(
            **(await super().to_dict()),
            url=self.url,
            image_url=self.image_url,
            title=self.title,
            description=self.description,
            site_name=self.site_name,
            price=self.price,
            currency=self.currency,
            image_id=self.image_id,
            image=image   
        )
    

class PageMetadataOverride(Base):
    image_url: Mapped[str | None]
    title: Mapped[str | None]
    description: Mapped[str | None]
    site_name: Mapped[str | None]
    price: Mapped[str | None]
    currency: Mapped[str | None]

    image_id: Mapped[int | None] = mapped_column(ForeignKey('metadataimage.id'))
    image: Mapped[Optional['MetadataImage']] = relationship('MetadataImage', lazy='raise')

    async def to_schema(self) -> schemas.PageMetadataOverride:
        image = None

        try:
            if self.image is not None:
                image = await self.image.to_schema()
        except InvalidRequestError:
            pass

        return schemas.PageMetadataOverride(
            **(await super().to_dict()),
            image_url=self.image_url,
            title=self.title,
            description=self.description,
            site_name=self.site_name,
            price=self.price,
            currency=self.currency,
            image_id=self.image_id,
            image=image   
        )


class User(Base):
    username: Mapped[str] = mapped_column(index=True, unique=True)
    email: Mapped[str] = mapped_column(index=True, unique=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    hashed_password: Mapped[bytes]

    itemizes: Mapped[list['Itemize']] = relationship('Itemize', back_populates='user', lazy='raise')

    async def to_schema(self) -> schemas.User:
        itemizes = None

        try:
            if self.itemizes is not None:
                itemizes = [await itemize.to_schema() for itemize in self.itemizes]
        except InvalidRequestError:
            pass

        return schemas.User(
            **(await super().to_dict()),
            username=self.username,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            itemizes=itemizes,
        )


class Link(Base):
    url: Mapped[str] = mapped_column(index=True, unique=True)
    itemize_id: Mapped[int] = mapped_column(ForeignKey('itemize.id'))
    page_metadata_id: Mapped[int] = mapped_column(ForeignKey('pagemetadata.id'))
    page_metadata_override_id: Mapped[int | None] = mapped_column(ForeignKey('pagemetadataoverride.id'))
    page_metadata: Mapped['PageMetadata'] = relationship('PageMetadata', lazy='raise')
    page_metadata_override: Mapped[Optional['PageMetadataOverride']] = relationship('PageMetadataOverride', lazy='raise')
    itemize: Mapped['Itemize'] = relationship('Itemize', back_populates='links', lazy='raise')

    async def to_schema(self) -> schemas.Link:
        page_metadata = None
        itemize = None
        page_metadata_override = None

        try:
            if self.page_metadata is not None:
                page_metadata = await self.page_metadata.to_schema()
        except InvalidRequestError:
            pass

        try:
            if self.itemize is not None:
                itemize = await self.itemize.to_schema()
        except InvalidRequestError:
            pass

        try:
            if self.page_metadata_override is not None:
                page_metadata_override = await self.page_metadata_override.to_schema()
        except InvalidRequestError:
            pass

        return schemas.Link(
            **(await super().to_dict()),
            url=self.url,
            itemize_id=self.itemize_id,
            page_metadata_id=self.page_metadata_id,
            page_metadata_override_id=self.page_metadata_override_id,
            page_metadata=page_metadata,
            page_metadata_override=page_metadata_override,
            itemize=itemize,
        )


class Itemize(Base):
    name: Mapped[str]
    slug: Mapped[str] = mapped_column(index=True)
    description: Mapped[str | None]
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    public: Mapped[bool] = mapped_column(default=False)
    user: Mapped[User] = relationship('User', back_populates='itemizes', lazy='raise')
    links: Mapped[list[Link]] = relationship('Link', back_populates='itemize', lazy='raise')

    async def to_schema(self, *, link_query: str | None = None) -> schemas.Itemize:
        user = None
        links = None

        try:
            if self.user is not None:
                user = await self.user.to_schema()
        except InvalidRequestError:
            pass

        try:
            if self.links is not None:
                links = [
                    await link.to_schema() for link in self.links
                    if link_query is None or (link.page_metadata is not None and (
                        link_query in (link.page_metadata.title or '').lower()
                        or link_query in (link.page_metadata.description or '').lower()
                        or link_query in (link.page_metadata.site_name or '').lower()
                        or link_query in (link.page_metadata.url or '').lower()
                    ))
                ]
        except InvalidRequestError:
            pass

        return schemas.Itemize(
            **(await super().to_dict()),
            name=self.name,
            slug=self.slug,
            description=self.description,
            user_id=self.user_id,
            public=self.public,
            user=user,
            links=links,
        )
