## Description

This project provides a set of repository classes designed to interact with a MongoDB database containing news articles and their associated metadata. The repository classes abstract the data access layer, providing a clean API for creating, retrieving, updating, and deleting articles, along with managing article embeddings and topic assignments.

## Overview

- `collections.py` - Defines constants for MongoDB collection names used throughout the project. This helps ensure consistency when accessing collections in the database.

- `connection.py` - Manages the connection to the MongoDB database, providing a centralized location for setting up and accessing the database client.

### Repositories

- `base.py` - This module contains a base repository class that provides common functionality and connection management for MongoDB. Other repository classes extend this base class to ensure consistent database operations across the project.

- `articles.py` - This module defines the `ArticlesRepository` class, responsible for managing CRUD operations on news articles.

- `article_embeddings.py` - This module contains the `ArticleEmbeddingsRepository` class, which manages CRUD operations for article embeddings.

- `topic_assignments.py` - This module provides the `TopicAssignmentsRepository` class, which handles the assignment of topics to articles.

- `topic_embeddings.py` - This module includes the `TopicEmbeddingsRepository` class, responsible for CRUD operations on topic embeddings.

## Usage

Below is an example of how to use the `ArticlesRepository` class to manage news articles in the database:

```python
from pulsespotter.db.repositories.articles import ArticlesRepository

# Initialize the repository
repo = ArticlesRepository() # environment="development" by default

# Retrieve an article by ID
article = repo.get_article_by_id(article_id)
print("Retrieved article:", article)

# Update an article
success = repo.update_article(article_id, {"title": "Updated Sample Article"})
print("Update success:", success)

# Delete an article
success = repo.delete_article(article_id)
print("Delete success:", success)
