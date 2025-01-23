import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set in environment variables!")

ALGORITHM = os.getenv("ALGORITHM", "HS256")  # Algorithm can have a default
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
