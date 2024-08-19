# File: docker/ingestion/Dockerfile

# Use the official Python image as a base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy relevant files and folders
RUN mkdir -p pulsespotter
COPY ./pulsespotter/db ./pulsespotter/db
COPY ./pulsespotter/ingestion ./pulsespotter/ingestion
COPY ./pulsespotter/utils ./pulsespotter/utils
COPY ./pulsespotter/__init__.py ./pulsespotter/
COPY ./pulsespotter/config.py ./pulsespotter/
COPY ./docker/ingestion/requirements.txt ./requirements.txt
COPY ./docker/ingestion/entrypoint.sh ./entrypoint.sh

# Install any dependencies specified in a requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Set environment variables
ENV PYTHONPATH=/app
# ENV MONGO_HOST=<MONGO_HOST>
# ENV ZENROWS_API_KEY=<ZENROWS_API_KEY>
ENV ENVIRONMENT=development

# Specify the command to run the ingestion process
ENTRYPOINT ["./entrypoint.sh"]
