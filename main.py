# main.py

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.auth import router as auth_router
from app.upload_profile import router as profile_router


# --------------------------------------------------
# CREATE APP
# --------------------------------------------------

app = FastAPI(
    title="TaskFlow API",
    version="1.0.0",
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# CREATE UPLOAD FOLDER
# --------------------------------------------------

os.makedirs(
    "uploads/profile_images",
    exist_ok=True,
)


# --------------------------------------------------
# SERVE PROFILE IMAGES
# --------------------------------------------------

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)


# --------------------------------------------------
# INCLUDE ROUTES
# --------------------------------------------------

app.include_router(auth_router)
app.include_router(profile_router)


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get("/")
async def home():
    return {
        "message": "TaskFlow API is running successfully."
    }


@app.get("/health")
async def health_check():
    return {
        "status": "ok"
    }