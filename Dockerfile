# Use an official Python runtime as a parent image
FROM python:3.13

# Copy the uv package manager and its binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy requirements first for better caching
COPY app/pyproject.toml .

# Install dependencies and ensure they're in PATH
RUN uv lock && \
    uv pip install --system uvicorn && \
    uv sync --locked

# Copy the application code
COPY app/ .

# Make port 80 available to the world outside this container
EXPOSE 8018

# Run the application using python -m to ensure we use the installed package
CMD ["uv", "run","main.py"]
