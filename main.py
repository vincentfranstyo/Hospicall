from fastapi import FastAPI

from call_logs import router as call_router
from db.supabase import create_supabase_client
from emergency_call import router as emergency_call_router
from healthcare import router as healthcare_router

app = FastAPI()
supabase_client = create_supabase_client()

app.include_router(call_router, prefix='/call')
app.include_router(healthcare_router, prefix='/healthcare')
app.include_router(emergency_call_router, prefix='/emergency')


@app.get("/")
async def root():
    return {"This is a one-call-away hospital line"}
