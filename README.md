# Image-processing-FastAPI

This project is focused on the accurate and efficient classification/Processing of face images...


# Build and start the services
podman image build -t image-processing -f ContainerFile 


podman run image-processing:latest  

# To test the endpoint:
curl -X POST -F "file=@/path/to/your/image.jpg" http://localhost:8000/upload
#### API Documentation
The API documentation provides details about the available endpoints, request and response formats, and example usage. You can access the documentation by visiting the /docs endpoint after starting the server (http://localhost:8000/docs).

