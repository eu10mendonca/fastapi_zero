from fastapi import FastAPI

from fastapi_zero.routers import auth, users
from fastapi_zero.schemas import Message

app = FastAPI(title="Minha API com FastAPI", version="1.0.0")


app.include_router(users.router)
app.include_router(auth.router)


@app.get(path="/", response_model=Message)
def read_root():
    return {"message": "Hello World!"}
