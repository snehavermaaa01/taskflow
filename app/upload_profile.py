import os
import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException,
)

from app.database import users_collection
from app.deps import get_current_user


router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
)


UPLOAD_DIR = Path("uploads/profile_images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

MAX_FILE_SIZE = 5 * 1024 * 1024


# GET CURRENT PROFILE
@router.get("/me")
async def get_my_profile(
    current_user: dict = Depends(get_current_user),
):
    return {
        "success": True,
        "id": str(current_user["_id"]),
        "name": current_user["name"],
        "email": current_user["email"],
        "profile_image": current_user.get("profile_image"),
    }


# UPLOAD OR UPDATE PROFILE PICTURE
@router.post("/upload")
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    # Check image type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG, and WEBP images are allowed.",
        )

    # Read image
    image_data = await file.read()

    if not image_data:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    # Check file size
    if len(image_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image must be smaller than 5 MB.",
        )

    # Generate unique filename
    extension = ALLOWED_CONTENT_TYPES[file.content_type]
    filename = f"{uuid.uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / filename

    # Save new image
    with open(file_path, "wb") as buffer:
        buffer.write(image_data)

    image_url = f"/uploads/profile_images/{filename}"

    # Get old image path
    old_profile_image = current_user.get("profile_image")

    # Update MongoDB
    await users_collection.update_one(
        {"_id": current_user["_id"]},
        {
            "$set": {
                "profile_image": image_url,
            }
        },
    )

    # Delete old image after successful update
    if old_profile_image:
        old_filename = os.path.basename(old_profile_image)
        old_file_path = UPLOAD_DIR / old_filename

        if old_file_path.exists():
            try:
                os.remove(old_file_path)
            except OSError:
                pass

    return {
        "success": True,
        "message": "Profile picture updated successfully.",
        "profile_image": image_url,
    }


# DELETE ONLY PROFILE PICTURE
@router.delete("/image")
async def delete_profile_image(
    current_user: dict = Depends(get_current_user),
):
    profile_image = current_user.get("profile_image")

    if not profile_image:
        raise HTTPException(
            status_code=404,
            detail="No profile picture found.",
        )

    # Get filename
    filename = os.path.basename(profile_image)
    file_path = UPLOAD_DIR / filename

    # Delete image from folder
    if file_path.exists():
        try:
            os.remove(file_path)
        except OSError:
            pass

    # Remove image path from MongoDB
    await users_collection.update_one(
        {"_id": current_user["_id"]},
        {
            "$set": {
                "profile_image": None,
            }
        },
    )

    return {
        "success": True,
        "message": "Profile picture deleted successfully.",
    }