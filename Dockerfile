FROM python:3.13

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN apt update && apt install -y ffmpeg
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "Hazel"]