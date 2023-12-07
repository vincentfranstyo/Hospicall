import json


def write_user_file(filename, users):
    with open(filename, 'w') as user_file:
        json.dump(users, user_file, indent=4)


def write_call_file(filename, call):
    with open(filename, 'w') as call_file:
        json.dump(call, call_file, indent=4)


def write_app_file(filename, app):
    with open(filename, 'w') as app_file:
        json.dump(app, app_file, indent=4)


def write_hf_file(filename, hf):
    with open(filename, 'w') as hf_file:
        json.dump(hf, hf_file, indent=4)
