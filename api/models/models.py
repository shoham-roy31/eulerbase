import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import (
    Annotated,
    Union
)

class User(BaseException):
    username : Annotated[str,"Username of the User"]

class UserIn(User):
    password : Annotated[str,"User Password"]

class UserDB(User):
    hashed_password : Annotated[str,"Hashed Password Of User"]
    shelf_life : Annotated[datetime,"Freshness"] = datetime.now().isoformat()

class UserRotate(UserIn):
    new_password : Annotated[str,"New Password for the User"]

class UserOut(User):
    token_type : Annotated[str,"Token Type"] = "Bearer"
    token : Annotated[str,"Authetication Token"]

class UserRenew(BaseModel):
    username : Annotated[str,"Username of the User"]
    new_shelf_life : Annotated[datetime, "New Shelf Life for the User"]

class ServerStatus(BaseModel):
    status : Annotated[str,"Status of the API"] = "API is Running"
    server_date : Annotated[datetime,"Current Server Date and Time"] = datetime.now().isoformat()

class HTTPError(BaseModel):
    status_code : Annotated[int,"Server Response Status Code"]
    detail : Annotated[str,"Description of Error"]

class ChatRequest(BaseModel):
    context : Annotated["str","Context for Chat API"]
    # vector_index_name : Annotated[Union[str,None],"Vector Index Name of the Chat API"] = None
    session_id : Annotated[Union[str,None],"Session ID"] = uuid.uuid4()

class ChatResponse(BaseModel):
    response : Annotated[str,"Response from Chat API"]
    token_generate_time : Annotated[datetime,"Resposne Generation Timestamp"]
    metadata : Annotated[ChatRequest,"Metadata Context"]