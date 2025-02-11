# Riva Speech Integration Setup

1. Start the Riva container:
   ```bash
   # Option 1: Using docker run
   docker run -it --rm --name=riva-speech \
      --runtime=nvidia \
      --gpus '"device=0"' \
      --shm-size=8GB \
      -e NGC_API_KEY \
      -e NIM_MANIFEST_PROFILE \
      -e NIM_HTTP_API_PORT=9000 \
      -e NIM_GRPC_API_PORT=50051 \
      -p 9000:9000 \
      -p 50051:50051 \
      -e NIM_OPTIMIZE=True \
      nvcr.io/nim/nvidia/riva-speech:latest

   # Option 2: Using docker-compose
   docker-compose up
   ```

2. Install Python dependencies:
   ```bash
   pip install grpcio nvidia-riva-client
   ```

3. Start the application:
   ```bash
   python app.py
   ```

4. Open http://localhost:8000/static/index.html in your browser
