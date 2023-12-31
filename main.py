from fastapi import FastAPI
from Utils.call_logs import calls as call_router
from Utils.healthcare import healthcares as healthcare_router
from Utils.emergency_call import emergencies as emergency_call_router
from Utils.auth import router as auth_router
from Utils.users import user as user_router
from Utils.appointment import appointment as appointment_router
from Utils.appointment_calls import appointment_calls as app_call_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(call_router, prefix='/call')
app.include_router(healthcare_router, prefix='/healthcare')
app.include_router(emergency_call_router, prefix='/emergency')
app.include_router(user_router, prefix='/user')
app.include_router(appointment_router, prefix='/appointment')
app.include_router(app_call_router, prefix='/appointment_calls')
app.include_router(auth_router)


@app.get("/")
async def root():
    return {"This is a one-call-away hospital line"}
