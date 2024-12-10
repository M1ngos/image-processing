from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
from datetime import datetime
import aiofiles
import logging
import face_recognition
from pymongo import MongoClient
from scipy.spatial.distance import cosine
from PIL import Image, ExifTags

# Configure logging
logger = logging.getLogger(__name__)

# Database setup
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

def fix_orientation(image_path):
    try:
        img = Image.open(image_path)
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = img._getexif()
        if exif is not None:
            orientation = exif.get(orientation)
            if orientation == 3:
                img = img.rotate(180, expand=True)
            elif orientation == 6:
                img = img.rotate(270, expand=True)
            elif orientation == 8:
                img = img.rotate(90, expand=True)
        img.save(image_path)  # Save the corrected image
    except Exception as e:
        logger.error(f"Error fixing orientation: {e}")

async def upload_image(file: UploadFile = File(...)):
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        # Save the file
        async with aiofiles.open(filepath, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
                        
        fix_orientation(filepath)

        # Extract facial features
        image = face_recognition.load_image_file(filepath)
        face_encodings = face_recognition.face_encodings(image)
        
        if not face_encodings:
            logger.info(f"No face detected in {filename}")
            raise HTTPException(status_code=400, detail="No face detected in the uploaded image")
        
        uploaded_encoding = face_encodings[0]
        
        # Check for matching face in database
        existing_faces = collection.find()
        for face in existing_faces:
            stored_encoding = face['features']
            similarity = 1 - cosine(uploaded_encoding, stored_encoding)
            
            # If similarity is above a certain threshold, consider it a match
            if similarity > 0.6:  # Adjust threshold as needed
                logger.info(f"Matching face found for {filename}")
                return JSONResponse(
                    content={
                        "message": "Face already exists in the database",
                        "similarity": similarity
                    },
                    status_code=409
                )
        
        # Store new face in database
        face_data = {
            "filename": filename,
            "features": uploaded_encoding.tolist()  # Convert numpy array to list
        }
        collection.insert_one(face_data)
        logger.info(f"Stored new face data for: {filename}")
        
        return JSONResponse(
            content={
                "message": "Image uploaded and processed successfully",
                "features_stored": True
            },
            status_code=200
        )
    
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def health_check():
    return {"status": "healthy"}
