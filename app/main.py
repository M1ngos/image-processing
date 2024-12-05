# app/main.py
from typing import Union
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
from datetime import datetime
import aiofiles
import logging
import face_recognition
from pymongo import MongoClient
from PIL import Image as PILImage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Image Upload Service w/ MongoDB")

MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "image_database"
COLLECTION_NAME = "face_features"

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI)
    client.server_info()  # To check the connection
    logger.info("Connected to MongoDB successfully.")
except Exception as e:
    logger.error(f"MongoDB connection failed: {str(e)}")
    raise HTTPException(status_code=500, detail="Database connection failed")

db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        async with aiofiles.open(filepath, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        with PILImage.open(filepath) as img:
            logger.info(f"Original image mode: {img.mode}")
            if img.mode != 'RGB':
                img = img.convert('RGB')
                img.save(filepath)  # Save the converted image back to the file
                logger.info(f"Image converted to RGB mode")

        with PILImage.open(filepath) as img:
            # Remove metadata and convert to RGB
            img = img.convert('RGB')
            img.save(filepath, format='JPEG', quality=95)  # Save with standard quality to avoid any problematic metadata


        # Load the image with face_recognition
        image = face_recognition.load_image_file(filepath)
        face_encodings = face_recognition.face_encodings(image)
        
        if not face_encodings:
            raise HTTPException(status_code=400, detail="No face detected in the uploaded image")
        
        face_data = {
            "filename": filename,
            "features": face_encodings[0].tolist()  # Convert numpy array to list for MongoDB
        }
        collection.insert_one(face_data)
        
        logger.info(f"Successfully processed and stored face data for: {filename}")
        
        return JSONResponse(
            content={"message": "Image uploaded and processed successfully", "features_stored": True},
            status_code=200
        )
    
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}