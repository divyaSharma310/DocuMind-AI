FROM python:3.12

WORKDIR /code

# Environment variables for Python pathing
ENV PYTHONPATH=/code/backend
ENV PORT=7860

# Rebuild trigger
ENV REBUILD_VERSION=2.0

COPY ./backend/requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./backend /code/backend

# Create a place for the DB and ensure it's writable
RUN mkdir -p /code/backend/faiss_data && chmod 777 /code/backend/faiss_data

EXPOSE 7860

# Run with explicit folder context
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]