FROM python:3.13-alpine
WORKDIR /app
COPY app.py .
ENV PYTHONUNBUFFERED=1
EXPOSE 8080
ENTRYPOINT ["python3", "/app/app.py"]
