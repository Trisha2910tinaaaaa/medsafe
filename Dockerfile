# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy everything from your project folder into the container's working directory
COPY . .

# Install all Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the ports your apps will run on
# Port 8501 is for Streamlit
# Port 8000 is for FastAPI
EXPOSE 8501
EXPOSE 8000

# The command to run when the container starts
# This runs both servers simultaneously in the background
CMD uvicorn main:app --host 0.0.0.0 --port 8000 & streamlit run app.py --server.port 8501 --server.address 0.0.0.0