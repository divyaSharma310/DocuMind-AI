# Use Python 3.12
FROM python:3.12

# Set working directory
WORKDIR /code

# Copy requirements first to leverage Docker cache
COPY ./backend/requirements.txt /code/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the backend code
COPY ./backend /code/backend

# Set environment variable to find local modules
ENV PYTHONPATH=/code/backend

# Expose the port Hugging Face expects
EXPOSE 7860

# Run the app (Hugging Face uses port 7860)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]