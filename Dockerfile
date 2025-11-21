FROM python:3.14-alpine

LABEL org.opencontainers.image.title="DuplexScanOCR"
LABEL org.opencontainers.image.version="1.1.2"
LABEL org.opencontainers.image.source=https://github.com/AngryBananer/DuplexScanOCR
LABEL org.opencontainers.image.description="Watches the /data/consume folder for pdf's and ocr's them. If the filename contains duplex, the script waites for a second pdf and combines them."

ARG TESSERACT_VERSION="5.5.0-r2"
ARG GHOSTSCRIPT_VERSION="10.05.1-r0"

ARG OCRMYPDF_VERSION="16.12.0"
ARG WATCHDOG_VERSION="6.0.0"
ARG PYPDF_VERION="6.3.0"

ARG DEFAULT_LANG="deu"

RUN apk add --update --no-cache \
    tesseract-ocr=${TESSERACT_VERSION} \
    tesseract-ocr-data-eng=${TESSERACT_VERSION} \
    tesseract-ocr-data-${DEFAULT_LANG}=${TESSERACT_VERSION} \
    ghostscript=${GHOSTSCRIPT_VERSION} \
    && pip install --no-cache-dir \
    watchdog==${WATCHDOG_VERSION} \
    ocrmypdf==${OCRMYPDF_VERSION} \
    pypdf==${PYPDF_VERION} \
    && mkdir /app

ENV TESSERACT_VERSION=${TESSERACT_VERSION}
ENV DEFAULT_LANG=${DEFAULT_LANG}

WORKDIR /app

COPY consumer.py /app/consumer.py

ENTRYPOINT ["python", "consumer.py"]