# Image-processing-FastAPI

This project is focused on the accurate and efficient classification/Processing of face images...

# Requirements

-- Installing on Mac or Linux --
First, make sure you have dlib already installed with Python bindings https://gist.github.com/ageitgey/629d75c1baac34dfa5ca2a1928a7aeaf :


### Build and start the services

# Podman:
podman image build -t image-processing -f ContainerFile 

# Docker:
docker build -t image-upload-service .
docker run -p 8000:8000 -p 27017:27017 image-upload-service

# MongoDB Volume: Add a volume to persist MongoDB data:
docker run -v mongo_data:/data/db -p 8000:8000 -p 27017:27017 image-upload-service


podman run image-processing:latest  

# To test the endpoint:
curl -X POST -F "file=@/path/to/your/image.jpg" http://localhost:8000/upload
#### API Documentation
The API documentation provides details about the available endpoints, request and response formats, and example usage. You can access the documentation by visiting the /docs endpoint after starting the server (http://localhost:8000/docs).

## Debugging
uvicorn app.main:app --host 0.0.0.0 --reload --log-level debug

