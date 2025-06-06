# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY ./app/pyproject.toml /app/

# Install any needed packages specified in pyproject.toml
RUN pip install "uvicorn[standard]" "fastapi" "sqlmodel" "psycopg2-binary" "cohere" "sentence-transformers" "numpy" "faker" "python-dotenv" "sqlalchemy-schemadisplay"

# Copy the rest of the application code into the container at /app
COPY . /app

# Make port 80 available to the world outside this container
EXPOSE 80

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
