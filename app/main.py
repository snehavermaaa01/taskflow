from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId

from app.database import (
    users_collection,
    projects_collection,
    check_database
)

from app.schemas import (
    SignupRequest,
    LoginRequest,
    UserResponse,
    TokenResponse,
    ProjectCreate,
    ProjectResponse
)

from app.security import (
    hash_password,
    verify_password,
    create_access_token
)

from app.deps import get_current_user


app = FastAPI(
    title="TaskFlow API",
    description="Task management API using FastAPI and MongoDB",
    version="1.0.0"
)


# -------------------------
# CORS
# -------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# ROOT
# -------------------------

@app.get("/")
def root():
    return {
        "message": "TaskFlow API is running"
    }


# -------------------------
# HEALTH
# -------------------------

@app.get("/health")
def health():

    if check_database():
        return {
            "api": "ok",
            "database": "MongoDB connected"
        }

    return {
        "api": "ok",
        "database": "MongoDB disconnected"
    }


# =====================================================
# AUTHENTICATION
# =====================================================

@app.post(
    "/auth/signup",
    response_model=UserResponse
)
def signup(data: SignupRequest):

    existing_user = users_collection.find_one({
        "email": data.email
    })

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = hash_password(data.password)

    user = {
        "email": data.email,
        "username": data.username,
        "password": hashed_password
    }

    result = users_collection.insert_one(user)

    return {
        "id": str(result.inserted_id),
        "email": data.email,
        "username": data.username
    }


# -------------------------
# LOGIN
# -------------------------

@app.post(
    "/auth/login",
    response_model=TokenResponse
)
def login(data: LoginRequest):

    user = users_collection.find_one({
        "email": data.email
    })

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        data.password,
        user["password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(
        str(user["_id"])
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# -------------------------
# CURRENT USER
# -------------------------

@app.get(
    "/users/me",
    response_model=UserResponse
)
def get_me(
    current_user=Depends(get_current_user)
):

    return {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "username": current_user["username"]
    }


# =====================================================
# PROJECTS
# =====================================================

# CREATE PROJECT
# =====================================================

@app.post(
    "/projects",
    response_model=ProjectResponse
)
def create_project(
    data: ProjectCreate,
    current_user=Depends(get_current_user)
):

    project = {
        "name": data.name,
        "description": data.description,
        "owner_id": str(current_user["_id"])
    }

    result = projects_collection.insert_one(project)

    return {
        "id": str(result.inserted_id),
        "name": project["name"],
        "description": project["description"],
        "owner_id": project["owner_id"]
    }


# =====================================================
# GET ALL PROJECTS
# =====================================================

@app.get(
    "/projects",
    response_model=list[ProjectResponse]
)
def get_projects(
    current_user=Depends(get_current_user)
):

    owner_id = str(current_user["_id"])

    projects = projects_collection.find({
        "owner_id": owner_id
    })

    result = []

    for project in projects:

        result.append({
            "id": str(project["_id"]),
            "name": project["name"],
            "description": project.get("description"),
            "owner_id": project["owner_id"]
        })

    return result


# =====================================================
# GET SINGLE PROJECT
# =====================================================

@app.get(
    "/projects/{project_id}",
    response_model=ProjectResponse
)
def get_project(
    project_id: str,
    current_user=Depends(get_current_user)
):

    try:
        project = projects_collection.find_one({
            "_id": ObjectId(project_id),
            "owner_id": str(current_user["_id"])
        })
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid project ID"
        )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return {
        "id": str(project["_id"]),
        "name": project["name"],
        "description": project.get("description"),
        "owner_id": project["owner_id"]
    }


# =====================================================
# UPDATE PROJECT
# =====================================================

@app.put(
    "/projects/{project_id}",
    response_model=ProjectResponse
)
def update_project(
    project_id: str,
    data: ProjectCreate,
    current_user=Depends(get_current_user)
):

    try:
        result = projects_collection.update_one(
            {
                "_id": ObjectId(project_id),
                "owner_id": str(current_user["_id"])
            },
            {
                "$set": {
                    "name": data.name,
                    "description": data.description
                }
            }
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid project ID"
        )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    project = projects_collection.find_one({
        "_id": ObjectId(project_id)
    })

    return {
        "id": str(project["_id"]),
        "name": project["name"],
        "description": project.get("description"),
        "owner_id": project["owner_id"]
    }


# =====================================================
# DELETE PROJECT
# =====================================================

@app.delete("/projects/{project_id}")
def delete_project(
    project_id: str,
    current_user=Depends(get_current_user)
):

    try:
        result = projects_collection.delete_one({
            "_id": ObjectId(project_id),
            "owner_id": str(current_user["_id"])
        })
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid project ID"
        )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return {
        "message": "Project deleted successfully"
    }