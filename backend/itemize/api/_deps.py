import jwt

from itemize import schemas
from itemize import models

from itemize.config import CONFIG
from itemize.db import DB

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer

from typing import Annotated


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/users/login')


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> schemas.DBUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
    )

    try:
        payload = jwt.decode(token, CONFIG.JWT_SECRET, algorithms=[CONFIG.JWT_ALGORITHM])
        user_id = payload.get('sub')
        if not isinstance(user_id, int):
            raise credentials_exception
        async with DB.async_session() as session:
            user = await session.get(models.User, user_id)
            if user is None:
                raise credentials_exception
            return schemas.DBUser(
                id=user.id,
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
            )
    except:
        raise credentials_exception


CurrentUser = Annotated[schemas.DBUser, Depends(get_current_user)]


async def match_username_slug(request: Request, user: CurrentUser):
    if request.path_params['username'] != user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to access this resource!',
        )

MatchUsernameSlug = Depends(match_username_slug)
