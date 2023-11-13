from fastapi import FastAPI
from Utils.call_logs import router as call_router
from Utils.healthcare import router as healthcare_router
from Utils.emergency_call import router as emergency_call_router
from Utils.auth import router as auth_router

app = FastAPI()

app.include_router(call_router, prefix='/call')
app.include_router(healthcare_router, prefix='/healthcare')
app.include_router(emergency_call_router, prefix='/emergency')
app.include_router(auth_router)


@app.get("/")
async def root():
    return {"This is a one-call-away hospital line"}
