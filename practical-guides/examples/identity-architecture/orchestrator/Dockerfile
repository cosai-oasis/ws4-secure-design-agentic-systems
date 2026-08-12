FROM docker.io/python:3.11-slim
WORKDIR /app
COPY server.py .
USER 65534:65534
CMD ["python3", "server.py"]
