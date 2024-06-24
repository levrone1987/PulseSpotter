#Dockerfile
FROM apache/airflow:2.6.0-python3.10

# Install additional dependencies
# USER root
COPY requirements.txt ./requirements.txt
# USER airflow
RUN pip install --user --upgrade pip
RUN pip install --no-cache-dir --user -r ./requirements.txt