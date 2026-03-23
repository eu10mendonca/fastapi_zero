from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.models import User
from fastapi_zero.schemas import FilterPage, Message, UserList, UserPublic, UserSchema
from fastapi_zero.security import get_current_user, get_password_hash, get_session

router = APIRouter(prefix="/users", tags=["users"])


T_Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
async def create_user(user: UserSchema, session: T_Session):
    db_user = User(**user.model_dump())

    try:
        db_user.password = get_password_hash(user.password)
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return db_user
    except IntegrityError as e:
        constraint = getattr(
            getattr(e.orig, "__cause__", None), "constraint_name", None
        )
        await session.rollback()
        if constraint == "uq_users_username":
            raise HTTPException(HTTPStatus.CONFLICT, "Username já cadastrado")
        if constraint == "uq_users_email":
            raise HTTPException(HTTPStatus.CONFLICT, "Email já cadastrado")

        raise HTTPException(HTTPStatus.CONFLICT, "Violação de integridade")


@router.get("/", status_code=HTTPStatus.OK, response_model=UserList)
async def read_users(
    session: T_Session,
    current_user: CurrentUser,
    filter_users: Annotated[FilterPage, Query()],
):
    # Essa linha valida o objeto de retorno com os modelos pydantic
    query = await session.scalars(
        Select(User).limit(filter_users.limit).offset(filter_users.offset)
    )

    users = query.all()
    return {"users": users}
    # return UserList(users=[UserPublic(**user.model_dump()) for user in database])
    # return {"users": database}


@router.get("/{user_id}", response_model=UserPublic)
async def read_user_by_id(user_id: int, session: T_Session, current_user: CurrentUser):
    user_db = await session.scalar(Select(User).where(User.id == user_id))
    if not user_db:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail="User not found")

    return user_db


@router.put("/{user_id}", response_model=UserPublic)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: T_Session,
    current_user: CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(HTTPStatus.FORBIDDEN, detail="Not enough permissions")
    try:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = user.password

        session.add(current_user)
        await session.commit()
        await session.refresh(current_user)

        return current_user

    except IntegrityError as e:
        constraint = getattr(
            getattr(e.orig, "__cause__", None), "constraint_name", None
        )
        await session.rollback()

        if constraint == "uq_users_username":
            raise HTTPException(HTTPStatus.CONFLICT, "Username já cadastrado")
        if constraint == "uq_users_email":
            raise HTTPException(HTTPStatus.CONFLICT, "Email já cadastrado")

        raise HTTPException(HTTPStatus.CONFLICT, "Violação de integridade")


@router.delete("/{user_id}", response_model=Message)
async def delete_user(
    user_id: int,
    current_user: CurrentUser,
    session: T_Session,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not enough permissions"
        )

    await session.delete(current_user)
    await session.commit()

    return {"message": "User deleted"}
