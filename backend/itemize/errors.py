from fastapi import Request, status
from fastapi.responses import JSONResponse


class BaseError(Exception):
    __match_args__ = ("msg",)

    def __init__(self, msg: str) -> None:
        super().__init__(msg)
        self.msg = msg


class ItemizeError(BaseError):
    pass


class ItemizeExistsError(ItemizeError):
    pass


class ItemizeNotFoundError(ItemizeError):
    pass


class ItemizeLinkNotFoundError(ItemizeError):
    pass


class MetadataError(BaseError):
    pass


class MetadataUnprocessableError(MetadataError):
    pass


class ImageNotFoundError(ItemizeError):
    pass


class UserError(BaseError):
    pass


class UserNotFoundError(UserError):
    pass


class UserExistsError(UserError):
    pass


class InvalidUsernameError(UserError):
    pass


class InvalidCredentialsError(UserError):
    pass


async def handle_fastapi_exception(r: Request, e: BaseError) -> JSONResponse:
    match e:
        case ItemizeExistsError(msg):
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT, content={"detail": msg}
            )
        case ItemizeNotFoundError(msg):
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"detail": msg}
            )
        case ItemizeLinkNotFoundError(msg):
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"detail": msg}
            )
        case MetadataUnprocessableError(msg):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST, content={"detail": msg}
            )
        case InvalidUsernameError(msg):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST, content={"detail": msg}
            )
        case InvalidCredentialsError(msg):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": msg}
            )
        case UserExistsError(msg):
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT, content={"detail": msg}
            )
        case UserNotFoundError(msg):
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"detail": msg}
            )
        case ImageNotFoundError(msg):
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content={"detail": msg}
            )
        case _:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": e.msg, "type": type(e).__name__},
            )
