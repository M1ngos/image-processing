from datetime import datetime, timedelta
import random
from fastapi import Depends
from app.utils.utils import verify_token


# Helper function to generate random timestamps and times
def generate_mock_date_and_time():
    now = datetime.now()
    future_date = now + timedelta(days=random.randint(1, 30))  # Random date within the next 30 days
    time = f"{random.randint(8, 15):02}:00"  # Random hour between 08:00 and 18:00
    return int(future_date.timestamp()), time

APPOINTMENTS = [
    {
        "id": 1,
        "type": "RENOVACAO",
        "status": "SCHEDULED",
        "date": generate_mock_date_and_time()[0],  # Unix timestamp
        "time": generate_mock_date_and_time()[1],  # Time as string (HH:mm)
        "license_id": "12345678",
    },
    {
        "id": 2,
        "type": "SEGUNDA VIA",
        "status": "SCHEDULED",
        "date": generate_mock_date_and_time()[0],  # Unix timestamp
        "time": generate_mock_date_and_time()[1],  # Time as string (HH:mm)
        "license_id": "87654321",
    },
]

async def get_appointments(token_data: dict = Depends(verify_token)):
    license_id = token_data.get("sub")  # Extracting license_id from token payload
    if not license_id:
        return {"appointments": []}
    
    # Filter appointments for the logged-in driver's license_id
    driver_appointments = [appt for appt in APPOINTMENTS if appt["license_id"] == license_id]
    return {"appointments": driver_appointments}