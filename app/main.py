from fastapi import FastAPI
from app.image_routes import upload_image
from app.main_routes import health_check
from app.schemas.user_schema import LoginResponse
from app.services.appointment_route import get_appointments
from app.services.ocr import IDDataResponse, extract_id_data
from app.services.user_routes import login
# from app.services.appointment_route import get_appointments
import logging, os

# Configure logging to show logs in the console
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more detailed logs
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Your logger instance
logger = logging.getLogger(__name__)

# Create the FastAPI app
app = FastAPI(title="Mobile Data capture API w/ MongoDB")

# Add routes
app.get("/health")(health_check)
# app.get("/secure-endpoint")()
app.post("/upload")(upload_image)
# app.post("/extract-data")(extract_data)
# app.get("/extract-data/face-image/{session_id}")(get_face_image)
app.post("/auth/login", response_model=LoginResponse)(login)
app.get("/driver/appointments")(get_appointments)
app.post("/extract-id-data/", response_model=IDDataResponse)(extract_id_data)
