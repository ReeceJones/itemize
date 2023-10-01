import pydantic


class BaseModel(pydantic.BaseModel):
    pass


class APIRequest(BaseModel):
    pass


class APIResponse(BaseModel):
    pass


class PageMetadata(BaseModel):
    url: str
    image_url: str
    title: str
    description: str
    site_name: str


class DBPageMetadata(PageMetadata):
    id: int


class Link(BaseModel):
    id: int
    url: str
    page_metadata: PageMetadata


class PageMetadataRequest(APIRequest):
    urls: list[str]


class PageMetadataResponse(APIResponse):
    metadatas: list[PageMetadata]


class User(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str


class DBUser(User):
    id: int


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


class Itemize(BaseModel):
    name: str
    slug: str
    description: str | None
    owner: str
    links: list[Link]


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
