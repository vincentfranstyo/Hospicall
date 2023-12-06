import json
import random
import randomtimestamp
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, validator, Field

from Utils.api_psychos import get_psychologist_list

call_logs_json = 'Data/call_logs.json'
health_facilities_json = 'Data/health_facilities.json'

with open(call_logs_json, "r") as read_call_file:
    call_logs = json.load(read_call_file)

with open(health_facilities_json, "r") as read_hf_file:
    health_facilities = json.load(read_hf_file)


def get_random_psychos(num_of_psychos: int):
    psycho_list_this_fac = []
    psycho_list = get_psychologist_list()

    for i in range(num_of_psychos):
        psycho_list_this_fac.append(random.randint(1, len(psycho_list)))
    return psycho_list_this_fac


class CallLog(BaseModel):
    call_id: str = Field(default_factory=lambda: str(len(health_facilities)))
    call_date: str = datetime.now().strftime("%Y-%m-%d")
    call_time: str = datetime.now().strftime("%H:%M:%S")
    caller_number: str = "unknown"
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
    facility_id: str = Field(default_factory=lambda: str(len(health_facilities)))
    facility_name: str
    facility_type: str
    address: Address
    coordinates: Coordinate
    phone_number: str
    bed_capacity: int
    doctor_count: int
    psychologist_count: int = random.randint(1, 6)
    psychologist_list: List[int] = get_random_psychos(psychologist_count)


class FacilityUpdate(BaseModel):
    facility_name: Optional[str]
    facility_type: Optional[str]
    address: Optional[Address]
    phone_number: Optional[str]
    bed_capacity: Optional[int]
    doctor_count: Optional[int]
    psychologist_count: Optional[int]
    psychologist_list: Optional[List[int]]