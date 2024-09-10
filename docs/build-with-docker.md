# Build the application with Docker

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