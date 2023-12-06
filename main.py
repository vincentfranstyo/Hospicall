from fastapi import FastAPI
from Utils.call_logs import calls as call_router
from Utils.healthcare import healthcares as healthcare_router
from Utils.emergency_call import emergencies as emergency_call_router
from Utils.auth import router as auth_router
from Utils.users import user as user_router

app = FastAPI()

app.include_router(call_router, prefix='/call')
app.include_router(healthcare_router, prefix='/healthcare')
app.include_router(emergency_call_router, prefix='/emergency')
app.include_router(user_router, prefix='/user')
app.include_router(auth_router)


@app.get("/")
async def root():
    return {"This is a one-call-away hospital line"}
