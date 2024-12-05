import os
import face_recognition
from pymongo import MongoClient

# MongoDB setup
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "image_database"
COLLECTION_NAME = "face_features"

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Directory to process
IMAGE_DIR = "face_images"

def process_directory(directory):
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if not os.path.isfile(filepath) or not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue
        
        try:
            # Load image and extract features
            image = face_recognition.load_image_file(filepath)
            face_encodings = face_recognition.face_encodings(image)
            
            if not face_encodings:
                print(f"No face detected in {filename}")
                continue
            
            # Store features in MongoDB
            face_data = {
                "filename": filename,
                "features": face_encodings[0].tolist()  # Convert numpy array to list for MongoDB
            }
            collection.insert_one(face_data)
            print(f"Processed and stored features for {filename}")
        
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    process_directory(IMAGE_DIR)
