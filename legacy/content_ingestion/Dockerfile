FROM apache/airflow:2.9.2-python3.10

# Set environment variables
ENV AIRFLOW_HOME=/opt/airflow

# Set the working directory
WORKDIR $AIRFLOW_HOME

# Copy the requirements file into the container
COPY requirements.txt .

# Install any additional packages if needed
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Copy the entrypoint script and give it execution rights
COPY entrypoint.sh /entrypoint.sh
# RUN chmod +x /entrypoint.sh

# Use the custom entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

# Expose ports
EXPOSE 8080 8793
