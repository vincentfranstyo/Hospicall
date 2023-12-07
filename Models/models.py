import json
import random
import randomtimestamp
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, validator, Field

from Utils.api_psychos import get_psychologist_list
from Utils.read_file import read_hf_file, read_user_file, read_call_file, read_appointment_file

call_logs_json = 'Data/call_logs.json'
health_facilities_json = 'Data/health_facilities.json'
appointment_json = 'Data/appointment.json'
users_json = 'Data/users.json'


psychos = get_psychologist_list()
health_facilities = read_hf_file(health_facilities_json)
users = read_user_file(users_json)
call_logs = read_call_file(call_logs_json)
appointments = read_appointment_file(appointment_json)


async def get_user_data(user_id: str):
    for user in users:
        if user.id == user_id:
            return user

    return None


async def get_hf(hf_id: str):
    for hf in health_facilities:
        if hf.id == hf_id:
            return hf

    return None


def get_psycho(psycho_id: str):
    for psycho in psychos:
        if psycho.id == psycho_id:
            return psycho

    return None


def get_random_psychos(num_of_psychos: int):
    psycho_list_this_fac = []
    psycho_list = psychos

    i = 0
    while i < num_of_psychos:
        random_psycho_id = random.randint(1, len(psycho_list))
        psycho_list_this_fac.append(random_psycho_id) if random_psycho_id not in psycho_list_this_fac else None
        i += 1

    return psycho_list_this_fac


class CallLog(BaseModel):
    call_id: str = str(len(call_logs) + 1)
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
    facility_id: str = str(len(health_facilities) + 1)
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


class Appointment(BaseModel):
    appointment_id: str = Field(default_factory=lambda: str(len(appointments) + 1))
    user_id: str
    psychologist_id: str
    health_facility_id: str
    attended_status: str = Field(default_factory=lambda: "false")


class AppointmentUpdate(BaseModel):
    pyschologist_id: Optional[str]
    health_facility_id: Optional[str]
    attended_status: Optional[str]
