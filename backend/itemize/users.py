import bcrypt
import jwt

import itemize.models as models
import itemize.schemas as schemas
import re

from itemize.config import CONFIG
from itemize.errors import InvalidUsernameError, UserExistsError, InvalidCredentialsError

from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime, timedelta


USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_]{3,20}$')
EMAIL_REGEX = re.compile(r'^\S+@\S+\.\S+$')


def is_email(email: str) -> bool:
    return EMAIL_REGEX.match(email) is not None


async def check_email_exists(session: AsyncSession, email: str) -> bool:
    existing_user = await session.scalar(
        select(
            func.count()
        )
        .select_from(models.User)
        .where(
            models.User.email == email,
        )
    ) or 0

    return existing_user > 0
    

async def check_username_exists(session: AsyncSession, username: str) -> bool:
    if not USERNAME_REGEX.match(username):
        raise InvalidUsernameError('Invalid username!')

    existing_user = await session.scalar(
        select(
            func.count()
        )
        .select_from(models.User)
        .where(
            models.User.username == username,
        )
    ) or 0

    return existing_user > 0


async def create_user(session: AsyncSession, username: str, email: str, password: str, first_name: str, last_name :str) -> None:
    if not USERNAME_REGEX.match(username):
        raise InvalidUsernameError('Invalid username!')

    existing_user = await session.scalar(
        select(
            func.count()
        )
        .select_from(models.User)
        .where(
            or_(
                models.User.username == username,
                models.User.email == email,
            )
        )
    ) or 0

    if existing_user > 0:
        raise UserExistsError('Username or Email already in use!')

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    user = models.User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        first_name=first_name,
        last_name=last_name,
    )
    session.add(user)
    await session.commit()


async def login_user(session: AsyncSession, username_or_email: str, password: str) -> tuple[str, schemas.User]:
    user = await session.scalar(
        select(models.User)
        .where(
            or_(
                models.User.username == username_or_email,
                models.User.email == username_or_email,
            )
        )
    )

    if user is None:
        raise InvalidCredentialsError('Username, email, or password may be incorrect!')
    
    if not bcrypt.checkpw(password.encode('utf-8'), user.hashed_password):
        raise InvalidCredentialsError('Username, email, or password may be incorrect!')
    
    return (
        jwt.encode({
            "sub": user.id,
            "username": user.username,
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(minutes=CONFIG.JWT_EXPIRATION_MINUTES),
        }, CONFIG.JWT_SECRET, algorithm=CONFIG.JWT_ALGORITHM),
        await user.to_schema(),
    )
