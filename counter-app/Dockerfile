FROM python:3.9-slim

WORKDIR /app

# Copy the app code
COPY app /app

# Copy the database file into the container's /app directory
COPY counter.db /app/counter.db

RUN pip install flask flask-cors

EXPOSE 3001

CMD ["python", "server.py"]
