FROM python:alpine

LABEL org.opencontainers.image.title="DuplexScanOCR"
LABEL org.opencontainers.image.version="1.1.1"
LABEL org.opencontainers.image.source=https://github.com/AngryBananer/DuplexScanOCR
LABEL org.opencontainers.image.description="Watches the /data/consume folder for pdf's and ocr's them. If the filename contains duplex, the script waites for a second pdf and combines them."

RUN apk add --update --no-cache \
    tesseract-ocr \
    ghostscript \
    tesseract-ocr-data-eng \
    tesseract-ocr-data-deu \
    && pip install --no-cache-dir \
    watchdog \
    ocrmypdf \
    pypdf \
    && mkdir /app

WORKDIR /app

COPY consumer.py /app/consumer.py

ENTRYPOINT ["python", "consumer.py"]