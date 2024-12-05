
from PIL import Image
import face_recognition

image_path = 'uploads/captured_image.jpg'

try:
    # Open the image using Pillow and convert it to RGB
    with Image.open(image_path) as img:
        img = img.convert('RGB')
        img.save(image_path, format='JPEG', quality=95)  # Re-save to ensure compatibility

    # Load the image for processing with face_recognition
    image = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(image, model='cnn')  # Use the CNN model for more accurate detection
    # face_encodings = face_recognition.face_encodings(image)

    if face_encodings:
        print("Face encoding found!")
    else:
        print("No faces detected.")
except Exception as e:
    print(f"Error: {e}")

