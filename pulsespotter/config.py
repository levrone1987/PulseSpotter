import os

from pathlib import Path

# Project-level constants
PROJECT_DIR = Path(__file__).parent.resolve()
DEV_DATABASE = "insightfinder-dev"

# Environment variables
MONGO_HOST = os.getenv("MONGO_HOST")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ZENROWS_API_KEY = os.getenv("ZENROWS_API_KEY")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
