from fastapi import FastAPI
from app.routes import upload_image, health_check, extract_data, get_face_image
import logging

# Configure logging to show logs in the console
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more detailed logs
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Your logger instance
logger = logging.getLogger(__name__)

# Create the FastAPI app
app = FastAPI(title="Image Upload Service w/ MongoDB")

# Add routes
app.post("/upload")(upload_image)
app.get("/health")(health_check)
app.post("/extract-data")(extract_data)
app.get("/extract-data/face-image/{session_id}")(get_face_image)

