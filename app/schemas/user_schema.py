from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class AppointmentType(str, Enum):
    RENOVACAO = "RENOVACAO"
    SEGUNDA_VIA = "SEGUNDA_VIA"

class AppointmentStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class Appointment(BaseModel):
    id: int
    type: AppointmentType
    date: int  # Unix timestamp to match Android app
    time: str
    status: AppointmentStatus

    @property
    def formatted_date(self) -> str:
        return datetime.fromtimestamp(self.date / 1000.0).strftime("%d.%m.%Y")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "type": "RENOVACAO",
                "date": 1705123200000,
                "time": "14:30",
                "status": "SCHEDULED",
                "formatted_date": "13.01.2024"
            }
        }

class Driver(BaseModel):
    id: int
    license_id: str
    name: str
    date_of_birth: int  # Unix timestamp to match Android app

    @property
    def formatted_date_of_birth(self) -> str:
        return datetime.fromtimestamp(self.date_of_birth / 1000.0).strftime("%d.%m.%Y")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "license_id": "12345678",
                "name": "John Doe",
                "date_of_birth": 977270400000,
                "formatted_date_of_birth": "01.01.1980"
            }
        }

class LoginRequest(BaseModel):
    license_id: str = Field(pattern=r'^\d{1,8}$')  # Matches Android validation
    date_of_birth: int  # Unix timestamp

class LoginResponse(BaseModel):
    token: str
    driver: Driver
    # appointments: List[Appointment]

    model_config = {
        "json_schema_extra": {
            "example": {
                "token":"token",
                "driver": {
                    "id": 1,
                    "license_id": "12345678",
                    "name": "John Doe",
                    "date_of_birth": 315532800000,
                    "formatted_date_of_birth": "01.01.1980"
                }
                # ,
                # "appointments": [
                #     {
                #         "id": 1,
                #         "type": "RENOVACAO",
                #         "date": 1705123200000,
                #         "time": "14:30",
                #         "status": "SCHEDULED",
                #         "formatted_date": "13.01.2024"
                #     }
                # ]
            }
        }
    }
