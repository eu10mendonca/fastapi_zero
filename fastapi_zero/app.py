from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from fastapi_zero.schemas import Message

app = FastAPI()


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
