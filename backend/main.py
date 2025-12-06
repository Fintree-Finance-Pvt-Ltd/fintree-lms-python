from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.auth_admin import router as admin_auth_router
from routers.onboarding import router as onboarding_router
from routers.pan_verify import router as pan_verify_router
from routers.pan_upload import router as pan_upload_router
from dotenv import load_dotenv
from routers.customer_router import router as customer_router
from routers.aadhaar_router import router as aadhaar_router
from routers.experian_router import router as experian_router

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_auth_router)
app.include_router(onboarding_router)
app.include_router(pan_verify_router)
app.include_router(pan_upload_router)
app.include_router(customer_router)
app.include_router(aadhaar_router)
app.include_router(experian_router)

@app.get("/")
def root():
    return {"message": "Loan Backend API Running"}
