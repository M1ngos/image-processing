import os
import face_recognition
import logging
from PIL import Image
from pymongo import MongoClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB setup
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "image_database"
COLLECTION_NAME = "face_features"

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Directory to process
IMAGE_DIR = "data"


def preprocess_image(filepath):
    """Ensure image is in RGB format."""
    try:
        with Image.open(filepath) as img:
            return img.convert("RGB")  # Convert to RGB format
    except Exception as e:
        logger.error(f"Error preprocessing image {filepath}: {e}")
        return None


def process_directory(directory):
    if not os.path.exists(directory):
        logger.error(f"Directory '{directory}' does not exist.")
        return

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if not os.path.isfile(filepath) or not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue

        try:
            # Preprocess the image
            processed_image = preprocess_image(filepath)
            if processed_image is None:
                logger.warning(f"Skipping {filename} due to preprocessing error.")
                continue

            # Convert to numpy array for face_recognition
            image_array = face_recognition.load_image_file(filepath)

            # Extract face encodings
            face_encodings = face_recognition.face_encodings(image_array)

            if not face_encodings:
                logger.info(f"No face detected in {filename}")
                continue

            # Store all detected faces in MongoDB
            for i, encoding in enumerate(face_encodings):
                face_data = {
                    "filename": filename,
                    "face_index": i,
                    "features": encoding.tolist()  # Convert numpy array to list for MongoDB
                }
                collection.insert_one(face_data)
                logger.info(f"Processed and stored features for {filename}, face {i+1}")

        except FileNotFoundError:
            logger.error(f"File not found: {filename}")
        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    process_directory(IMAGE_DIR)
