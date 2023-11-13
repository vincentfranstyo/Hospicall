from datetime import datetime

import randomtimestamp
from pydantic import BaseModel, validator
from typing import Optional

from db.supabase_manager import create_supabase_client

supabase_client = create_supabase_client()


def get_calls():
    try:
        response = supabase_client.table("call_logs").select("*").execute()
        calls = response.data
        return calls
    except Exception as e:
        print(f"Error retrieving calls: {str(e)}")
        return {"message": "no data retrieved"}


class Coordinate(BaseModel):
    longitude: float
    latitude: float

    @validator('longitude')
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('longitude must be between -180 and 180')
        return v

    @validator('latitude')
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('latitude must be between -90 and 90')
        return v


class Address(BaseModel):
    street: str
    city: str
    province: str


class HealthFacility(BaseModel):
    id: str
    name: str
    type: str
    city: str
    street: str
    province: str
    longitude: float
    latitude: float
    phone_number: str
    bed_capacity: int
    doctor_count: int


class FacilityUpdate(BaseModel):
    name: Optional[str]
    type: Optional[str]
    city: Optional[str]
    street: Optional[str]
    province: Optional[str]
    longitude: Optional[float]
    latitude: Optional[float]
    phone_number: Optional[str]
    bed_capacity: Optional[int]
    doctor_count: Optional[int]


class CallLog(BaseModel):
    id: str
    call_date: str = datetime.now().strftime("%Y-%m-%d")
    call_time: str = datetime.now().strftime("%H:%M:%S")
    callee_number: str = "+6285365347656"
    call_duration: str = randomtimestamp.randomtimestamp().strftime("%H:%M:%S")
    call_status: str = "completed"
    caller_number: str = "+6285368768767"


class UpdateCall(BaseModel):
    call_date: Optional[str]
    call_time: Optional[str]
    callee_number: Optional[str]
    call_duration: Optional[str]
    call_status: Optional[str]
    caller_number: Optional[str]
