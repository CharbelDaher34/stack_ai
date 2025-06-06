# VectorDB API

This project is a REST API for indexing and querying documents in a Vector Database, built with Python, FastAPI, and SQLModel.

## Project Structure

The project follows a Domain-Driven Design (DDD) approach, separating concerns into three main layers:

-   `app/api`: The API layer, responsible for handling HTTP requests and responses. It uses FastAPI routers.
-   `app/services`: The service layer, containing the core business logic.
-   `app/infrastructure`: The infrastructure layer, responsible for interacting with external systems like the database and implementing the indexing algorithms. It includes repositories for data access.

This structure makes the application modular, easier to test, and maintain.

## Indexing Algorithms

The project implements three different vector indexing algorithms from scratch:

1.  **Linear Index (Brute Force):**
    -   **Description:** This index iterates through all the vectors in the database and calculates the distance to the query vector. It is the most basic approach.
    -   **Complexity:**
        -   Space: O(n*d)
        -   Time (search): O(n*d)
    -   **Use Case:** Best for small datasets where accuracy is critical and search time is not a major concern.

2.  **KD-Tree:**
    -   **Description:** A space-partitioning data structure for organizing points in a k-dimensional space. It allows for efficient nearest neighbor searches.
    -   **Complexity:**
        -   Space: O(n*d)
        -   Time (search): O(log n) on average for randomly distributed data.
    -   **Use Case:** Suitable for low to medium-dimensional data. Performance degrades as the number of dimensions increases.

3.  **Ball Tree:**
    -   **Description:** A space-partitioning data structure that partitions data into a set of nested hyperspheres. It is effective for high-dimensional data.
    -   **Complexity:**
        -   Space: O(n*d)
        -   Time (search): O(log n)
    -   **Use Case:** More efficient than KD-Trees for high-dimensional data, as it is less sensitive to the "curse of dimensionality".

## Concurrency

To handle concurrent requests, the application uses the following strategies:

-   **Database:** The API uses SQLAlchemy's connection pooling and provides a separate database session for each request. This is a standard and reliable way to manage concurrent database access.
-   **In-Memory Indexes:** Access to the shared, in-memory vector indexes is protected by a `threading.Lock`. This ensures that only one thread can modify or read from the indexes at a time, preventing data races.

## How to Run the Project

### Using Docker

1.  **Build the Docker image:**
    ```bash
    docker build -t vectordb-api .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -p 80:80 -e POSTGRES_USER=... -e POSTGRES_PASSWORD=... -e POSTGRES_SERVER=... -e POSTGRES_PORT=... -e POSTGRES_DB=... vectordb-api
    ```
    (You will need to replace the environment variables with your PostgreSQL connection details)

### Local Development

1.  **Install dependencies:**
    ```bash
    pip install -r app/requirements.txt 
    ```
    (Note: you might need to generate a requirements.txt from pyproject.toml first)

2.  **Set up environment variables:**
    Create a `.env` file in the `app` directory with your database credentials.

3.  **Run the application:**
    ```bash
    uvicorn app.main:app --reload
    ```

## How to Run Tests

1.  **Install test dependencies:**
    ```bash
    pip install pytest
    ```

2.  **Run tests:**
    ```bash
    pytest app/tests
    ``` 