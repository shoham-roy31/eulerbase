import hashlib
import datetime
from ..models import (
    UserDB,
    UserOut,
    UserRenew,
    HTTPError
)
from typing import Dict
from pathlib import Path 
from fastapi import status
from fastapi.security import OAuth2PasswordBearer

THREE_DAYS = 36 * 3600
DB = Path(__file__).resolve().parent / "DB"

def read_db(path : str) -> Dict[str,str]:
    user_data = dict()
    with open(path,'r') as f:
        data = f.read()
    for line in data.splitlines():
        k,v = data.split("=",
                         maxsplit = 1
                         )
        user_data[k] = v
    return user_data

def write_db(path : str,
            data : Dict[str,str]
            ) -> None:
    content = [] 
    for k,v in data.items():
        content.append(f"{k}={v}")
    content = '\n'.join([c for c in content])
    
    with open(path, 'w') as f:
        f.write(content)

def hash(password : str
         ) -> str:
    return hashlib.sha256(
        bytes(password,
              encoding = "utf-8"
              ).hexdigest()
    )

def generate_token(user_data : UserDB) -> str:
    return hash(user_data.username + user_data.shelf_life)

def getUserList(path : str) -> Dict[str,str]:
    user_dict = dict()
    for user in path.iterdir():
        if user.is_file():
            user_dict[user.name] = user
    return user_dict

USER_DICT = getUserList(DB)

def getUserDB(username : str) -> UserDB | HTTPError:
    try:
        print(f"Attempting to retrive user: {username}")
        assert USER_DICT[username]
        return UserDB(**read_db(username))
    
    except Exception as e:
        return HTTPError(status_code = 400,
                         detail = str(e)
                         )

def login(username:str,
          password:str
          ) -> UserOut | HTTPError:
    try:
        user_data = UserDB(username)
        assert isinstance(user_data,UserDB)
        assert hash(password) == user_data.hash_password
        return UserOut(
            username = user_data.username,
            token = generate_token(user_data)
        )
    except Exception as e:
        return HTTPError(
            status_code = 401,
            detail = "UNAUTHORIZED"
        )

    
        

        


