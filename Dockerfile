FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg fonts-dejavu fonts-noto-core ca-certificates && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir yt-dlp
RUN useradd --create-home --uid 10001 bayan && mkdir /data && chown bayan:bayan /data
WORKDIR /app
COPY worker.py start.py /app/
USER root
ENV BAYAN_DATA=/data PORT=8080
EXPOSE 8080
CMD ["python", "/app/start.py"]
