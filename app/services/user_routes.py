from fastapi import HTTPException
from datetime import datetime, date
from app.schemas.user_schema import LoginRequest, LoginResponse, Driver
import time

from app.utils.utils import create_access_token #HERE WHEN CALLED OR IMPORTED


async def login(request: LoginRequest):
    try:
        date_of_birth_temp = datetime.fromtimestamp(request.date_of_birth / 1000.0)
        if date_of_birth_temp > datetime.now():
            raise HTTPException(status_code=400, detail="Invalid date of birth")
    except (ValueError, OSError):
        raise HTTPException(status_code=400, detail="Invalid date format")

    # print("Debug credentials:"+request.license_id+","+str(request.date_of_birth))
    if request.license_id == "12345678" and request.date_of_birth == 977270400000:

        # Create a token
        token_data = {"sub": request.license_id}
        token = create_access_token(data=token_data)
        print("token:"+token)

        return {
            "token": token,
            "driver": {
                "id": 1,
                "license_id": request.license_id,
                "name": "John Doe",
                "date_of_birth": request.date_of_birth,
            }
        }
        
    if request.license_id == "87654321" and request.date_of_birth == 977270400000:

        # Create a token
        token_data = {"sub": request.license_id}
        token = create_access_token(data=token_data)
        print("token:"+token)

        return {
            "token": token,
            "driver": {
                "id": 1,
                "license_id": request.license_id,
                "name": "John Doe",
                "date_of_birth": request.date_of_birth,
            }
        }

    raise HTTPException(
        status_code=401,
        detail="Invalid license ID or date of birth"
    )
