from datetime import datetime


def create_user_document(
    email: str,
    username: str,
    hashed_password: str
):
    return {
        "email": email,
        "username": username,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow()
    }


def create_project_document(
    name: str,
    description: str,
    status: str,
    user_id: str
):
    return {
        "name": name,
        "description": description,
        "status": status,
        "user_id": user_id,
        "created_at": datetime.utcnow()
    }


def create_task_document(
    title: str,
    description: str,
    priority: int,
    status: str,
    project_id: str,
    user_id: str
):
    return {
        "title": title,
        "description": description,
        "priority": priority,
        "status": status,
        "project_id": project_id,
        "user_id": user_id,
        "created_at": datetime.utcnow()
    }