from itemize import schemas
from itemize import users
from itemize import errors

from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated


router = APIRouter(prefix='/users')


@router.post('')
async def create_user(req: schemas.CreateUserRequest = Body(...)) -> schemas.CreateUserResponse:
    await users.create_user(
        username=req.username,
        email=req.email,
        password=req.password,
        first_name=req.first_name,
        last_name=req.last_name
    )
    token, user = await users.login_user(req.username, req.password)
    
    return schemas.CreateUserResponse(
        user=user,
        token=token
    )


@router.get('/check/{username_or_email}')
async def check_username_or_email(username_or_email: str) -> None:
    is_email = users.is_email(username_or_email)
    print(f'{username_or_email} is email: {is_email}')
    if not is_email and await users.check_username_exists(username_or_email):
        raise errors.UserExistsError('Username already exists!')
    elif is_email and await users.check_email_exists(username_or_email):
        raise errors.UserExistsError('Email already exists!')


@router.post('/login')
async def login_user(req: Annotated[OAuth2PasswordRequestForm, Depends()]) -> schemas.Token:
    token, _ = await users.login_user(req.username, req.password)
    
    return schemas.Token(
        access_token=token
    )