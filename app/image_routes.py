import io
import logging
import os
import re
from datetime import datetime

import aiofiles
import face_recognition
import numpy as np
import pytesseract
from PIL import Image, ExifTags
from fastapi import UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from pymongo import MongoClient

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
            return JSONResponse(
                    content={
                        "message": "No face detected in the image",
                    },
                    status_code=400
                )
                # raise HTTPException(status_code=400, detail="No face detected in the uploaded image")
        
        
        uploaded_encoding = face_encodings[0]
        
        # Check for matching face in database
        existing_faces = collection.find()
        found_match = False
        max_similarity = 0

        for face in existing_faces:
            stored_encoding = np.array(face['features'])  # Convert stored list back to numpy array

            # Use face_recognition's built-in comparison instead of cosine similarity
            face_distances = face_recognition.face_distance([stored_encoding], uploaded_encoding)
            similarity = 1 - face_distances[0]  # Convert distance to similarity

            # Update maximum similarity found
            max_similarity = max(max_similarity, similarity)

            # If similarity is above threshold, consider it a match
            if similarity > 0.6:  # Threshold adjusted (lower is stricter)
                found_match = True
                logger.info(f"Matching face found for {filename} with similarity={similarity:.3f}")
                return JSONResponse(
                    content={
                        "message": "Face already exists in the database",
                        "similarity": float(similarity),  # Convert numpy float to Python float
                        "max_similarity_found": float(max_similarity)
                    },
                    status_code=409
                )

        # Store new face in database
        face_data = {
            "filename": filename,
            "features": uploaded_encoding.tolist(),  # Convert numpy array to list
            "upload_date": datetime.now()
        }
        collection.insert_one(face_data)
        logger.info(f"Stored new face data for: {filename}")

        return JSONResponse(
            content={
                "message": "Image uploaded and processed successfully",
                "features_stored": True,
                "max_similarity_found": float(max_similarity)  # Include highest similarity found
            },
            status_code=200
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



async def extract_data(front: UploadFile = File(...), back: UploadFile = File(...)):
    # Load images
    front_image = Image.open(io.BytesIO(await front.read()))
    back_image = Image.open(io.BytesIO(await back.read()))

       # Convert to OpenCV format
    front_cv_image = cv2.cvtColor(np.array(front_image), cv2.COLOR_RGB2BGR)

    # Perform OCR
    front_text = pytesseract.image_to_string(front_image)
    back_text = pytesseract.image_to_string(back_image)

    # Initialize the face cascade for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    # Convert the image to grayscale for face detection
    gray = cv2.cvtColor(front_cv_image, cv2.COLOR_BGR2GRAY)
    
    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(50, 50))

    if len(faces) == 0:
        return JSONResponse({"error": "No face detected in the image."}, status_code=400)

    # Extract the first detected face and resize it
    x, y, w, h = faces[0]
    face_image = front_cv_image[y:y+h, x:x+w]

    # Resize the face image to a larger size (e.g., 200x200)
    face_resized = cv2.resize(face_image, (200, 200))

    # Convert the resized face image back to PIL format
    face_pil = Image.fromarray(cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB))

    # Save the face image to a buffer
    face_buffer = io.BytesIO()
    face_pil.save(face_buffer, format="JPEG")
    face_buffer.seek(0)

    # Generate a unique identifier for the session
    session_id = str(uuid.uuid4())
    face_image_storage[session_id] = face_buffer

    # JSON data response
    data = {
        "front_text": front_text,
        "back_text": back_text,
        "face_image_url": f"/extract-data/face-image/{session_id}",
    }

    return JSONResponse({"data": data})


async def get_face_image(session_id: str):
    """Endpoint to return the face image based on a unique session ID."""
    if session_id not in face_image_storage:
        return JSONResponse({"error": "Invalid or expired session ID."}, status_code=404)

    # Retrieve and remove the buffer from storage for cleanup
    face_buffer = face_image_storage.pop(session_id)

    return StreamingResponse(face_buffer, media_type="image/jpeg")
