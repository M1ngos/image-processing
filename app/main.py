from fastapi import FastAPI
from app.routes import upload_image, health_check

# Create the FastAPI app
app = FastAPI(title="Image Upload Service w/ MongoDB")

# Add routes
app.post("/upload")(upload_image)
app.get("/health")(health_check)
