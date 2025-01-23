from fastapi import Depends

from app.utils.utils import verify_token

async def get_appointments(token_data: dict = Depends(verify_token)):
    return {"appointments": [{"id": 1, "type": "RENOVACAO", "status": "SCHEDULED"}]}
