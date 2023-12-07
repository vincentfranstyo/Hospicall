import json


def read_call_file(call_logs_json):
    with open(call_logs_json, "r") as read_file:
        call_logs = json.load(read_file)
    return call_logs


def read_hf_file(hf_json):
    with open(hf_json, "r") as read_file:
        health_facilities = json.load(read_file)
    return health_facilities


def read_user_file(users_json):
    with open(users_json, "r") as read_file:
        users = json.load(read_file)
    return users


def read_appointment_file(appointment_json):
    with open(appointment_json, "r") as read_file:
        appointments = json.load(read_file)
    return appointments
