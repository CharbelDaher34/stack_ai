# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Copy the uv package manager and its binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY app/pyproject.toml .

RUN uv lock
RUN uv sync --locked

COPY app/ /app

# Make port 80 available to the world outside this container
EXPOSE 8018

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8018","--workers", "3"]
