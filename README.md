# DuplexScanOCR

Watches the `/data/consume` folder for PDFs and OCRs them with [OCRmyPDF](https://github.com/ocrmypdf/OCRmyPDF). If the filepath contains `duplex`, the script waits for a second pdf file with `duplex` in the path and combines them. The finished files are exported to the `/data/export` folder.

## Environment variables

 - `DUPLEX_TIMEOUT=<seconds>`
 Sets the maximum time difference between importing the front scan and back scan. Defaults to 600 s.
 Should be longer than the time it takes to OCR the files.
