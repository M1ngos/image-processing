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
    # Sample ID condition (from the provided image)
    if request.license_id == "108497392" and request.date_of_birth == 478944000000:
        token_data = {"sub": request.license_id}
        token = create_access_token(data=token_data)
        return {
            "token": token,
            "driver": {
                "id": 2,
                "license_id": "108497392",
                "name": "Omar Ame Chande",
                "date_of_birth": 478944000000,
                "licence_number": "108497392",
                "issue_number": 2,
                "expiry_date": 1731283200000,
                "place_of_issue": "BEIRA",
                "gender": "MASCULINO",
                "restrictions": "0"
            }
        }

    # Existing test users (keep for backward compatibility)
    if request.license_id in ["12345678", "87654321"] and request.date_of_birth == 977270400000:
        token_data = {"sub": request.license_id}
        token = create_access_token(data=token_data)
        return {
            "token": token,
            "driver": {
                "id": 1,
                "license_id": request.license_id,
                "name": "Domingos Emanuel",
                "date_of_birth": request.date_of_birth,
                "licence_number": "12345678",
                "issue_number": 1,
                "expiry_date": 1893456000000,
                "place_of_issue": "MAPUTO",
                "gender": "MASCULINO",
                "restrictions": "0"
            }
        }

    raise HTTPException(status_code=401, detail="Invalid license ID or date of birth")
