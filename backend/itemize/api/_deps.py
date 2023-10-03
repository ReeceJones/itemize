import jwt

from itemize import schemas
from itemize import models

from itemize.config import CONFIG
from itemize.db import DB as _DB

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer

from typing import Annotated, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/users/login')


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with _DB.async_session() as session:
        yield session


DB = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: DB) -> schemas.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
    )

    try:
        payload = jwt.decode(token, CONFIG.JWT_SECRET, algorithms=[CONFIG.JWT_ALGORITHM])
        user_id = payload.get('sub')
        if not isinstance(user_id, int):
            raise credentials_exception
        user = await session.get(models.User, user_id)
        if user is None:
            raise credentials_exception
        return await user.to_schema()
    except:
        raise credentials_exception


CurrentUser = Annotated[schemas.User, Depends(get_current_user)]


async def match_username_slug(request: Request, user: CurrentUser):
    if request.path_params['username'] != user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to access this resource!',
        )

MatchUsernameSlug = Depends(match_username_slug)
