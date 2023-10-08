import pydantic

from datetime import datetime
from typing import Optional


class BaseModel(pydantic.BaseModel):
    pass


"""
Model schemas
"""


class DBModel(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime


class MetadataImage(DBModel):
    mime: str | None
    source_image_url: str | None
    url: str | None


class PageMetadata(DBModel):
    url: str
    image_url: str | None
    title: str | None
    description: str | None
    site_name: str | None
    price: str | None
    currency: str | None
    image_id: int | None
    image: MetadataImage | None


class PageMetadataOverride(DBModel):
    image_url: str | None
    title: str | None
    description: str | None
    site_name: str | None
    price: str | None
    currency: str | None
    image_id: int | None
    image: MetadataImage | None


class User(DBModel):
    username: str
    email: str
    first_name: str
    last_name: str
    itemizes: list['Itemize'] | None


class Link(DBModel):
    url: str
    itemize_id: int
    page_metadata_id: int
    page_metadata_override_id: int | None
    page_metadata: PageMetadata | None
    page_metadata_override: PageMetadataOverride | None
    itemize: Optional['Itemize']


class Itemize(DBModel):
    name: str
    slug: str
    description: str | None
    user_id: int
    public: bool
    user: User | None
    links: list[Link] | None


"""
API Schemas
"""


class APIRequest(BaseModel):
    pass


class APIResponse(BaseModel):
    pass


class CreateUserRequest(APIRequest):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str


class CreateUserResponse(APIResponse):
    user: User
    token: str


class Token(APIResponse):
    access_token: str
    token_type: str = 'bearer'


class PageMetadataRequest(APIRequest):
    urls: list[str]


class PageMetadataResponse(APIResponse):
    metadatas: list[PageMetadata]


class CreateItemizeRequest(APIRequest):
    name: str
    description: str | None


class CreateItemizeResponse(APIResponse):
    itemize: Itemize


class ListItemizesResponse(APIResponse):
    itemizes: list[Itemize]


class GetItemizeResponse(APIRequest):
    itemize: Itemize


class CreateLinkRequest(APIRequest):
    url: str


class CreateLinkResponse(APIResponse):
    link: Link


class UpdateLinkMetadataRequest(APIRequest):
    title: str | None
    description: str | None
    image_url: str | None
    site_name: str | None
    price: str | None
    currency: str | None


class UpdateLinkMetadataResponse(APIResponse):
    link: Link


class UpdateItemizeRequest(APIRequest):
    name: str | None
    description: str | None
    public: bool | None


class UpdateItemizeResponse(APIResponse):
    itemize: Itemize
