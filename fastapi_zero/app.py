from datetime import datetime, timezone
from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from fastapi_zero.schemas import Message, UserDB, UserList, UserPublic, UserSchema

database: list = []


app = FastAPI(title="Minha API com FastAPI", version="1.0.0")


@app.get("/", status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {"message": "Hello World!"}
    # return Message(message="Hello World!") também funciona


@app.get("/hello-world", status_code=HTTPStatus.OK, response_class=HTMLResponse)
def hello_world():
    return """
    <html>
        <head>
            <title>Hello World</title>
        </head>
        <body>
            <h1>Hello World!</h1>
        </body>
    </html>
    """


@app.post("/users/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema):
    user_with_id = UserDB(
        **user.model_dump(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        id=len(database) + 1
    )
    database.append(user_with_id)
    return user_with_id


@app.get("/users/", status_code=HTTPStatus.OK, response_model=UserList)
def read_users():
    # Essa linha valida o objeto de retorno com os modelos pydantic
    return UserList(users=[UserPublic(**user.model_dump()) for user in database])
    # return {"users": database}


@app.put("/users/{user_id}", response_model=UserPublic)
def update_user(user_id: int, user_updated: UserSchema):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

    for user in database:
        if user.model_dump().get("id") == user_id:
            user_updated = UserDB(
                **user_updated.model_dump(),
                created_at=user.model_dump().get("created_at"),
                updated_at=datetime.now(timezone.utc),
                id=user_id
            )
            database[user_id - 1] = user_updated
            return user_updated


@app.delete("/users/{user_id}", response_model=Message)
def delete_user(user_id: int):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

    del database[user_id - 1]

    return {"message": "User deleted"}
