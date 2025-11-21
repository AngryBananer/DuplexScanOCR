# DuplexScanOCR

This container adds two features to any scanner that can scan to network shares: duplex scanning and OCR (optical character recognition).

DuplexScanOCR watches the `/data/consume` folder for PDFs and OCRs them with [OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF). If the file path contains `duplex`, the script will wait for a second PDF file with `duplex` in the path and combine them. The finished files are exported to the `/data/export` folder.
Subfolders are recreated inside the export folder.

## Environment Variables

 - `DUPLEX_TIMEOUT=<seconds>`
 Sets the maximum time difference between importing the front scan and back scan. Defaults to 600 s.
 Should be longer than the time it takes to OCR the files.

 - `OCR_LANG=<LangCode>`
 Sets the OCR language ocrmypdf/tesseract uses. Available [LangCodes](https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html).
 Defaults to German (deu).

- `LOGLEVEL=<log level>`
 Sets the log level. Defaults to `INFO`

 - `LOGFILE=<log file>`
 Sets the log file. If no log file is set, logging to a file is disabled.