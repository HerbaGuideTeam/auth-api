# Use the official Python image as a base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the local code to the container
COPY . .

# Install dependencies using pipenv
RUN pip install pipenv
RUN pipenv install --deploy --ignore-pipfile

# Expose the port your FastAPI app runs on
EXPOSE 8000

# Command to run the FastAPI application
CMD ["pipenv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
