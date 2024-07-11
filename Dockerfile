FROM jbarlow83/ocrmypdf-ubuntu

LABEL org.opencontainers.image.source=https://github.com/AngryBananer/DuplexScanOCR
LABEL org.opencontainers.image.description="Watches the /data/consume folder for pdf's and ocr's them. If the filename contains duplex, the script waites for a second pdf and combines them."

RUN apt-get update \
    && apt-get install --no-install-recommends pdftk -y \
    && apt-get clean \
    && pip install --no-cache-dir watchdog \
    && rm -rf /app/* \
    && rm -rf /var/lib/apt/lists/*

COPY consumer.py /app/consumer.py

ENTRYPOINT ["python", "consumer.py"]