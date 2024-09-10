
# Running with Docker

## Application
The application consists of:
- A FastAPI server which serves as a backend for the application.
- A Streamlit application serving as a frontend of the system.

### Running with Docker
Navigate to the `docker/app` directory in your terminal. Then run the following command:
```bash
docker-compose up --build
```
This will build both the backend and the frontend of the application.

#### Access the UI
You can start using the application by simply visiting:
```bash
http://localhost:8501
```
in your browser.

#### Access the API
You can check out the API docs by visiting:
```bash
http://localhost:8000/docs
```
in your browser.


## Ingestion
The ingestion process is a process of crawling news websites for news articles and then scraping each article for relevant content.
This includes the article title, description, date and paragraphs. The parsed content then gets persistently stored into our database.

### Creating the Docker image
Execute the following command from the project's root directory:
```bash
docker build -f docker/ingestion/Dockerfile -t ingestion-service .
```

### Example running the container
Execute the following command from the project's root directory:
```bash
docker run -it --rm -v $(pwd)/logs:/app/logs ingestion-service \
--start-date 2024-08-12 \
--end-date 2024-08-12 \
--page-limit 15
```
