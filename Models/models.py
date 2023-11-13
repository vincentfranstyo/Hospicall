import json

from pydantic import BaseModel, validator
from typing import Optional, Any
from datetime import datetime
import randomtimestamp


call_logs_json = 'Data/call_logs.json'

with open(call_logs_json, "r") as read_file:
    call_logs = json.load(read_file)


def get_call_ids():
    with open(call_logs_json, "r") as call_file:
        call_in_logs = json.load(call_file)
    return [call['call_id'] for call in call_in_logs]


class CallLog(BaseModel):
    call_id: str = str(int(get_call_ids()[-1]) + 1)
    call_date: str = datetime.now().strftime("%Y-%m-%d")
    call_time: str = datetime.now().strftime("%H:%M:%S")
    callee_number: str = "+6287890765"
    call_duration: str = randomtimestamp.randomtimestamp().strftime("%H:%M:%S")
    call_status: str = "completed"


class UpdateCall(BaseModel):
    call_date: Optional[str]
    call_time: Optional[str]
    callee_number: Optional[str]
    call_duration: Optional[str]
    call_status: Optional[str]


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
    facility_id: str = None
    facility_name: str
    facility_type: str
    address: Address
    coordinates: Coordinate
    phone_number: str
    bed_capacity: int
    doctor_count: int


class FacilityUpdate(BaseModel):
    facility_name: Optional[str]
    facility_type: Optional[str]
    address: Optional[Address]
    phone_number: Optional[str]
    bed_capacity: Optional[int]
    doctor_count: Optional[int]