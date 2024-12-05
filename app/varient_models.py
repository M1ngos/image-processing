import os
import logging
import face_recognition
from PIL import Image
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import aiofiles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Image Upload Service w/ MongoDB")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Generate unique filename using timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)

        # Save the file
        async with aiofiles.open(filepath, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        # Convert image to RGB format
        with Image.open(filepath) as img:
            img = img.convert('RGB')
            img.save(filepath, format='JPEG', quality=95)

        # Load image with face_recognition
        image = face_recognition.load_image_file(filepath)

        # Try detecting faces with different models
        try:
            face_encodings = face_recognition.face_encodings(image, model='cnn')
            logger.info("Using CNN model for face detection")
        except Exception as e:
            logger.warning(f"CNN model failed: {str(e)}")
            face_encodings = face_recognition.face_encodings(image, model='hog')
            logger.info("Falling back to HOG model for face detection")

        if not face_encodings:
            logger.warning("No faces detected in the image")
            raise HTTPException(status_code=400, detail="No faces detected in the uploaded image")

        # Log number of detected faces
        logger.info(f"Detected {len(face_encodings)} faces")

        # Return response
        return JSONResponse(
            content={
                "message": "Image uploaded and processed successfully",
                "faces_detected": len(face_encodings),
                "features_stored": True
            },
            status_code=200
        )

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
