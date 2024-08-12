
## Running with Docker

### Ingestion
The ingestion process is a process of crawling news websites for news articles and then scraping each article for relevant content.
This includes the article title, description, date and paragraphs. The parsed content then gets persistently stored into our database.

#### Creating the Docker image
Execute the following command from the project's root directory:
```bash
docker build -f docker/Dockerfile.ingestion -t ingestion-service .
```

#### Example running the container
Execute the following command from the project's root directory:
```bash
docker run -it --rm -v $(pwd)/logs:/app/logs ingestion-service \
--start-date 2024-08-12 \
--end-date 2024-08-12 \
--page-limit 15
```
