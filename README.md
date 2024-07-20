# DuplexScanOCR

Watches the `/data/consume` folder for PDFs and OCRs them with [OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF). If the filepath contains `duplex`, the script waits for a second pdf file with `duplex` in the path and combines them. The finished files are exported to the `/data/export` folder.

## Environment variables

 - `DUPLEX_TIMEOUT=<seconds>`
 Sets the maximum time difference between importing the front scan and back scan. Defaults to 600 s.
 Should be longer than the time it takes to OCR the files.

 - `OCR_LANG=<LangCode>`
 Sets the OCR language ocrmypdf/tesseract uses. Available [LangCodes](https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html).
 Defaults to german (deu).

- `LOGLEVEL=<log level>`
 Sets the log level. Defaults to `INFO`

 - `LOGFILE=<log file>`
 Sets the log file. If no logfile is set, logging to a file is disabled.