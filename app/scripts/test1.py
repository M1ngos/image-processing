import face_recognition
from PIL import Image

image_path = 'uploads/captured_image.jpg'
try:
    # Open the image and convert to RGB if necessary
    with Image.open(image_path) as img:
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(image_path)  # Save the converted image

    # Now load the image using face_recognition
    image = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(image)

    if face_encodings:
        print("Face encoding found!")
        print(face_encodings)
    else:
        print("No faces detected.")
except Exception as e:
    print(f"Error: {e}")
