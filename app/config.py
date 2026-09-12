import os
from pathlib import Path
from dotenv import load_dotenv

# Define the project root directory
BASE_DIR = Path(__file__).resolve().parent\


# Load the .env file explicitly from the project root
load_dotenv(dotenv_path=BASE_DIR / ".env")

class Config:
    """Centralized configuration class for the application."""
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    MONGO_URL: str = os.getenv("MONGO_URL", "")



# Instantiate a global config object for easy importing
config = Config()

MONGO_URL = config.MONGO_URL
SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM
