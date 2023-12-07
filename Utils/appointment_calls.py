import json
import sys

from fastapi import APIRouter, Depends

from Utils.api_psychos import get_psychologist_list
from Models.models import Coordinate, Appointment
from Models.user import UserJSON
from Utils.auth import get_current_user
from Utils.call_logs import create_call_log
from Utils.emergency_call import distance_by_long_and_lat
from Utils.healthcare import get_health_facility_by_id
from Utils.users import not_user, not_admin
from Utils.appointment import create_appointment, get_appointment_by_id
from Utils.read_file import read_hf_file

appointment_calls = APIRouter(tags=['Appointment Calls'])
url = 'https://ca-sereneapp.braveisland-f409e30d.southeastasia.azurecontainerapps.io/'

healthcare_json = "Data/health_facilities.json"
facilities = read_hf_file(healthcare_json)


@appointment_calls.get('/closest_fac')
async def get_closest_fac(longitude: float, latitude: float, user: UserJSON = Depends(get_current_user)):
    not_user(user)

    closest_fac = {}
    current_coor = Coordinate(longitude=longitude, latitude=latitude)
    current_distance = sys.maxsize

    for facility in facilities:
        facility_coor = Coordinate(longitude=facility['coordinates']['longitude'], latitude=facility['coordinates']['latitude'])
        dis = distance_by_long_and_lat(facility_coor, current_coor)

        if dis < current_distance:
            current_distance = dis
            closest_fac = facility

    return [{"Message": "Here is the closest health facility to you"}, {"closest_fac": closest_fac}]


@appointment_calls.get('/available_psychologists')
async def get_available_psychologists_based_on_facility(longitude: float, latitude: float, user: UserJSON = Depends(get_current_user)):
    not_user(user)

    closest_fac_res = await get_closest_fac(longitude=longitude, latitude=latitude, user=user)

    closest_fac = closest_fac_res[1]['closest_fac']
    psychos_id = closest_fac['psychologist_list']

    all_psychos = get_psychologist_list()
    list_of_psychos_in_fac = []

    for psycho in all_psychos:
        if psycho['psychologist_id'] in psychos_id:
            list_of_psychos_in_fac.append(psycho)

    return list_of_psychos_in_fac


@appointment_calls.post('/make_appointment')
async def make_appointment(add_appointment: Appointment, user: UserJSON = Depends(get_current_user)):
    not_user(user)
    made_appointment = await create_appointment(add_appointment=add_appointment, user=user)
    return made_appointment


@appointment_calls.post('/make_appointment_call')
async def make_appointment_call(appointment_id: str, user: UserJSON = Depends(get_current_user)):
    not_user(user)

    caller_number = user.dict()['phone_number']

    appointment = await get_appointment_by_id(appointment_id)
    hf_id = appointment['health_facility_id']

    hf = await get_health_facility_by_id(hf_id)
    callee_number = hf['phone_number']

    made_call = []
    if callee_number and caller_number:
        made_call = await create_call_log(callee_number=callee_number, caller_number=caller_number, user=user)

    return made_call
