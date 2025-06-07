# Vector Database REST API

This project is a REST API for indexing and querying documents within a custom-built Vector Database. It's designed to store and retrieve vector embeddings, which is essential for applications involving natural language processing, recommendation systems, and more.

## Features

*   **CRUD Operations**: Create, Read, Update, and Delete operations for Libraries, Documents, and Chunks.
*   **Vector Indexing**: Index the contents of a library for efficient similarity search.
*   **k-Nearest Neighbor (kNN) Search**: Perform kNN vector search over a selected library using an embedding query.
*   **Dockerized**: The entire application is containerized for easy deployment and scalability.
*   **Python SDK**: A client SDK is available for programmatic interaction with the API.

## Technical Choices

### Database

For the database, we chose **PostgreSQL** along with **SQLModel**.

*   **PostgreSQL**: A powerful, open-source object-relational database system with a strong reputation for reliability, feature robustness, and performance.
*   **SQLModel**: Provides a seamless way to interact with the database using Python objects, combining Pydantic and SQLAlchemy. This simplifies data validation and database operations.

### Indexing

We have implemented two indexing algorithms from scratch. Below is a detailed explanation of each.

#### Linear Index (`linear_index.py`)

The Linear Index is the most straightforward approach to similarity search. It iterates through every vector in the database, computes the distance to the query vector, and returns the top `k` nearest neighbors.

*   **Description**: This method provides guaranteed accuracy by performing a brute-force search. While simple to implement, its performance degrades linearly with the size of the dataset.
*   **Space Complexity**: `O(N * D)`, where `N` is the number of vectors and `D` is their dimension.
*   **Time Complexity**:
    *   **Search**: `O(N * D)` per query.
    *   **Add**: `O(D)` to append a vector.
    *   **Delete**: `O(N)` to find and remove a vector.

#### Ball Tree (`ball_tree.py`)

The Ball Tree is a more advanced data structure that partitions data into a series of nested hyperspheres ("balls"). This hierarchical structure allows for efficient searching by pruning entire branches of the tree that cannot possibly contain the nearest neighbors.

*   **Description**: By recursively dividing the data space, the Ball Tree avoids the need to compare the query vector with every single point, leading to significant performance gains on large datasets. However, its efficiency can decrease in very high-dimensional spaces (a phenomenon often called the "curse of dimensionality").
*   **Space Complexity**: `O(N * D)`, as it must store all vectors, plus a small overhead for the tree structure.
*   **Time Complexity**:
    *   **Build**: `O(N * D * log(N))`
    *   **Search (Average)**: `O(D * log(N))`
    *   **Search (Worst Case)**: `O(N * D)`
    *   **Add/Delete**: `O(D * log(N))` on average.

## Project Structure

```
.
├── app
│   ├── api -> Contains the FastAPI routers and dependencies.
│   ├── core -> Defines the core data models (Pydantic/SQLModel).
│   ├── infrastructure -> Manages data persistence (repositories) and indexing algorithms.
│   ├── services -> Implements the business logic for different components.
│   ├── tests -> Contains tests for the API and indexing algorithms.
│   ├── main.py -> The entry point for the FastAPI application.
│   └── pyproject.toml -> Project dependencies.
├── docker-compose.yml -> Defines the services, networks, and volumes for Docker.
├── Dockerfile -> Instructions to build the Docker image for the application.
├── client_sdk.py -> Sdk to interact with the api
├── example_sdk_usage.py -> How to use the api
└── README.md -> This file.
```

## Getting Started

### Prerequisites

*   Docker and Docker Compose
*   Python 3.13+ (if running without Docker)
*   PostgreSQL (if running without Docker)
*   uv

### Installation with Docker (Recommended)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/CharbelDaher34/stack_ai.git
    cd stack_ai
    ```

2.  **Start the services:**
    ```bash
    docker-compose up -d
    ```
    This will build the Docker image for the application and start the FastAPI server along with a PostgreSQL database instance. The API will be available at `http://localhost:8018`.

### Installation without Docker

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/CharbelDaher34/stack_ai.git
    cd stack_ai/app
    ```

2.  **Set up a PostgreSQL database.**

3.  **Create a `.env` file** in the `app` directory and add your database credentials. You need to add each field separately:
    ```env
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432
    POSTGRES_USER=<your_postgres_user>
    POSTGRES_PASSWORD=<your_postgres_password>
    POSTGRES_DB=<your_postgres_db>
    ```

4.  **Install dependencies:**
    ```bash
    uv sync
    ```

5.  **Run the application:**
    ```bash
    uv run python main.py
    ```
    The API will be available at `http://localhost:8018`.

## API Usage

You can interact with the API using any HTTP client or by using the provided Python SDK client (`client_sdk.py`).

See `example_sdk_usage.py` for a demonstration of how to use the SDK.

## Running Tests

To run the tests, you can use the following command from the `app` directory:
```bash
uv run python run_tests.py
``` 