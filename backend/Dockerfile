FROM python:3.13-slim

# llama-cpp-python has no prebuilt wheel for Python 3.13 yet — needs a toolchain
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Source files are mounted via volume in dev — COPY is for prod builds
COPY app/ ./app/
COPY app/migrations/ ./migrations/
COPY run.py .

EXPOSE 8000

CMD ["python", "run.py"]
