from fastapi import APIRouter, Depends, HTTPException, status
import json
from Models.user import UserJSON

from Models.models import HealthFacility, FacilityUpdate, Appointment, AppointmentUpdate
from Utils.auth import get_current_user
from Utils.users import not_user, not_admin
from Utils.read_file import read_appointment_file
from Utils.write_file import write_app_file

app_json = "Data/appointment.json"
appointment = APIRouter(tags=["Appointments"])

appointments = read_appointment_file(app_json)


def get_appointment_ids():
    return [appointment["appointment_id"] for appointment in appointments]


@appointment.get("/")
async def get_appointments(user: UserJSON = Depends(get_current_user)):
    not_user(user)
    return appointments


@appointment.get("/{appointment_id}")
async def get_appointment_by_id(appointment_id: str, user: UserJSON = Depends(get_current_user)):
    not_user(user)
    appointment_ids = get_appointment_ids()
    if appointment_id not in appointment_ids:
        return {"message": "The appointment does not exist"}

    for appointment in appointments:
        if appointment['appointment_id'] == appointment_id:
            return appointment
    return None


@appointment.post("/new_appointment")
async def create_appointment(add_appointment: Appointment, user: UserJSON = Depends(get_current_user)):
    not_user(user)

    add_appointment.user_id = user.id
    appointments.append(add_appointment.dict())
    write_app_file(app_json, appointments)

    return [{"message": "Appointment added successfully"}, {"Appointment": add_appointment}]


@appointment.put("/update_appointment")
async def update_health_appointment(appointment_id: str, update_app: AppointmentUpdate, user: UserJSON = Depends(get_current_user)):
    global appointment
    not_user(user)
    appointment_ids = get_appointment_ids()
    if appointment_id not in appointment_ids:
        return {"The appointment you are looking for is not available"}

    for appointment in appointments:
        if appointment['appointment_id'] == appointment_id:
            update_data = {key: value for key, value in update_app.dict().items() if value}
            appointment.update(update_data)

    write_app_file(app_json, appointments)

    return [{"message": "Appointment updated successfully"},{"Appointment": appointment}]


@appointment.delete('/delete_appointment')
async def delete_health_appointment(appointment_id: str, user: UserJSON = Depends(get_current_user)):
    not_user(user)
    global appointments
    appointment_ids = get_appointment_ids()
    if appointment_id not in appointment_ids:
        return {"message": "The appointment you are looking for is not available"}

    appointments_to_delete = []
    for appointment in appointments:
        if appointment['appointment_id'] == appointment_id:
            appointments_to_delete.append(appointment)
    if not appointments_to_delete:
        return {"message": "The appointment you are looking for is not available"}

    appointment_username = appointments_to_delete[0]['username']
    appointment_psychologist_name = appointments_to_delete[0]['psychologist_name']
    appointment_healthcare_name = appointments_to_delete[0]['health_facility_name']
    appointments = [appointment for appointment in appointments if appointment not in appointments_to_delete]

    write_app_file(app_json, appointments)

    return {"Message": "Appointment for " + appointment_username + "with  " + appointment_psychologist_name + " at " + appointment_healthcare_name + " deleted successfully"}
