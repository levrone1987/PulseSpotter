import os

from pathlib import Path

# Project-level constants
PROJECT_DIR = Path(__file__).parent.resolve()
RESOURCES_DIR = PROJECT_DIR.joinpath("resources")
RESOURCES_DIR.mkdir(parents=True, exist_ok=True)

# Environment variables
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_DATABASE = os.getenv("MONGO_DATABASE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ZENROWS_API_KEY = os.getenv("ZENROWS_API_KEY")
QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL")

__all__ = [
    "PROJECT_DIR",
    "RESOURCES_DIR",
    "MONGO_HOST",
    "MONGO_DATABASE",
    "OPENAI_API_KEY",
    "ZENROWS_API_KEY",
    "QDRANT_HOST",
    "QDRANT_API_KEY",
    "API_BASE_URL",
]
