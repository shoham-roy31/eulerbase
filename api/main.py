from api.models import (
    ChatRequest,
    ChatResponse,
    HTTPError
)
from typing import Annotated
from .controller import generate
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post('/chat')
async def chat(chat_req : Annotated[ChatRequest,"Chat Request Payload"]) -> ChatResponse | HTTPError:
    try:
        return await generate(chat_req)
    except Exception as e:
        raise HTTPException(status_code = 500,
                            detail = str(e)
                            )