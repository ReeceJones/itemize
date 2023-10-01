from sqlalchemy import select, Select, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr, relationship

from datetime import datetime


class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    

class PageMetadata(Base):
    url: Mapped[str] = mapped_column(index=True, unique=True)
    image_url: Mapped[str]
    title: Mapped[str]
    description: Mapped[str]
    site_name: Mapped[str]
    images: Mapped[list['MetadataImage']] = relationship('MetadataImage', lazy='raise')


class User(Base):
    username: Mapped[str] = mapped_column(index=True, unique=True)
    email: Mapped[str] = mapped_column(index=True, unique=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    hashed_password: Mapped[bytes]

    itemizes: Mapped[list['Itemize']] = relationship('Itemize', back_populates='user', lazy='raise')


class Link(Base):
    url: Mapped[str] = mapped_column(index=True, unique=True)
    itemize_id: Mapped[int] = mapped_column(ForeignKey('itemize.id'))
    page_metadata_id: Mapped[int] = mapped_column(ForeignKey('pagemetadata.id'))
    page_metadata: Mapped['PageMetadata'] = relationship('PageMetadata', lazy='raise')
    itemize: Mapped['Itemize'] = relationship('Itemize', back_populates='links', lazy='raise')


class Itemize(Base):
    name: Mapped[str]
    slug: Mapped[str] = mapped_column(index=True)
    description: Mapped[str | None]
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user: Mapped[User] = relationship('User', back_populates='itemizes', lazy='raise')
    links: Mapped[list[Link]] = relationship('Link', back_populates='itemize', lazy='raise')


class MetadataImage(Base):
    page_metadata_id: Mapped[int] = mapped_column(ForeignKey('pagemetadata.id'))
    data: Mapped[bytes]
