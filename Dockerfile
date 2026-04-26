# Use Python 3.12
FROM python:3.12

# Set working directory
WORKDIR /code

# Force Docker to rebuild from this point onwards
ENV REBUILD_DATE=2024-04-26

# Copy requirements first
COPY ./backend/requirements.txt /code/requirements.txt

# Install dependencies with NO CACHE
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the backend code
COPY ./backend /code/backend

# Set environment variable
ENV PYTHONPATH=/code/backend

# Run the app
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]