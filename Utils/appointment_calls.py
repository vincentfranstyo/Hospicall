import sys

from fastapi import APIRouter, Depends

from Models.models import Coordinate, Appointment, MakeAppointment
from Models.user import UserJSON
from Utils.api_psychos import get_psychologist_list, get_psycho_by_id
from Utils.appointment import create_appointment, get_appointment_by_id
from Utils.auth import get_current_user
from Utils.call_logs import create_call_log
from Utils.emergency_call import distance_by_long_and_lat
from Utils.healthcare import get_health_facility_by_id
from Utils.read_file import read_hf_file, read_appointment_file
from Utils.users import not_user

appointment_calls = APIRouter(tags=['Appointment Calls'])
url = 'https://ca-sereneapp.braveisland-f409e30d.southeastasia.azurecontainerapps.io/'

healthcare_json = "Data/health_facilities.json"
app_json = "Data/appointment.json"
facilities = read_hf_file(healthcare_json)
appointments = read_appointment_file(app_json)


@appointment_calls.get('/closest_fac')
async def get_closest_fac(longitude: float, latitude: float, user: UserJSON = Depends(get_current_user)):
    not_user(user)

    closest_fac = {}
    current_coor = Coordinate(longitude=longitude, latitude=latitude)
    current_distance = sys.maxsize

    for facility in facilities:
        facility_coor = Coordinate(longitude=facility['coordinates']['longitude'],
                                   latitude=facility['coordinates']['latitude'])
        dis = distance_by_long_and_lat(facility_coor, current_coor)

        if dis < current_distance:
            current_distance = dis
            closest_fac = facility

    return [{"Message": "Here is the closest health facility to you"}, {"closest_fac": closest_fac}]


@appointment_calls.get('/get_all_psychologists')
async def get_all_psychologists(user: UserJSON = Depends(get_current_user)):
    not_user(user)
    return get_psychologist_list()


@appointment_calls.get('/get_psychologists_by_id')
async def get_psychologist_by_id(psychologist_id: int, user: UserJSON = Depends(get_current_user)):
    not_user(user)

    psycho = get_psycho_by_id(psychologist_id)
    return psycho


@appointment_calls.get('/available_psychologists')
async def get_available_psychologists_based_on_facility(longitude: float, latitude: float, user: UserJSON = Depends(get_current_user)):
    not_user(user)

    closest_fac_res = await get_closest_fac(longitude=longitude, latitude=latitude, user=user)

    closest_fac = closest_fac_res[1]['closest_fac']
    psycho_ids = closest_fac['psychologist_list']

    all_psychos = get_psychologist_list()
    list_of_psychos_in_fac = []

    for psycho in all_psychos:
        if psycho['psychologist_id'] in psycho_ids:
            list_of_psychos_in_fac.append(psycho)

    return list_of_psychos_in_fac


@appointment_calls.get('/find_psychologists_location')
async def find_psychologists_location_by_id(psychologist_id: int, user: UserJSON = Depends(get_current_user)):
    not_user(user)
    facs_list = []
    for fac in facilities:
        if psychologist_id in fac['psychologist_list']:
            facs_list.append(fac)
    return facs_list


@appointment_calls.post('/make_appointment')
async def make_appointment(psychologist_id: str, health_facility_id: str, user: UserJSON = Depends(get_current_user)):
    not_user(user)
    add_appointment = MakeAppointment(user_id=user.dict()['id'], psychologist_id=psychologist_id, health_facility_id=health_facility_id)
    new_appointment = Appointment(
        appointment_id=add_appointment.dict()['appointment_id'],
        user_id=add_appointment.dict()['user_id'],
        psychologist_id=add_appointment.dict()['psychologist_id'],
        health_facility_id=add_appointment.dict()['health_facility_id'],
        attended_status=add_appointment.dict()['attended_status']
    )
    made_appointment = await create_appointment(add_appointment=new_appointment, user=user)
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

