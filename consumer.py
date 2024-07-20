import os
import shutil
import tempfile
from pathlib import Path
import subprocess
import pypdf
import ocrmypdf
import itertools as itt
from watchdog.observers.polling import PollingObserver
from watchdog.events import PatternMatchingEventHandler
import logging

CONSUME_FOLDER = "/data/consume/" #input folder
EXPORT_FOLDER = "/data/export/" #output folder

LOGLEVEL = os.environ.get('LOGLEVEL', "INFO").upper()
LOGFILE = os.environ.get('LOGFILE')

logger = logging.getLogger('consumer_logger')

if LOGFILE is not None:
    logging.basicConfig( #there must be a better solution to this
        level=LOGLEVEL,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOGFILE)
        ]
    )
    logger.info("Log file set to " + LOGFILE)
else:
    logging.basicConfig(
        level=LOGLEVEL,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )
    logger.info("Log file disabled")

logger.info("Log level set to " + LOGLEVEL)

OCR_LANG = os.environ.get('OCR_LANG', "deu")
logger.info("OCR language set to " + OCR_LANG)

DUPLEX_TIMEOUT = int(os.environ.get('DUPLEX_TIMEOUT', "600"))
logger.info("Duplex timeout set to " + str(DUPLEX_TIMEOUT))

waiting_folder = None
waiting_file = None

def on_pdf_created(event):
    inputfile= event.src_path
    logger.info(f"PDF-file '{inputfile}' has been created!")
    if "duplex" not in inputfile:
        logger.info("No duplex scan...")
        outputfile = EXPORT_FOLDER + "ocr_" + os.path.split(inputfile)[1]
        ocrFile(inputfile, outputfile)
    else:
        logger.info("Duplex scan!")
        outputfile = waiting_folder + "ocr_" + os.path.split(inputfile)[1]
        if not ocrFile(inputfile, outputfile):
            return
        global waiting_file
        if waiting_file is None:
            waiting_file = outputfile
        elif DUPLEX_TIMEOUT > 0 and os.path.getmtime(outputfile) - os.path.getmtime(waiting_file) > DUPLEX_TIMEOUT:
            logger.warning(f"Waiting file '{waiting_file}' is older than {str(DUPLEX_TIMEOUT)} seconds, deleting and waiting with current file.")
            try:
                os.remove(waiting_file)
            except OSError:
                pass
            waiting_file = outputfile
        else:
            logger.info("Combinig scans...")
            duplexfile = EXPORT_FOLDER + os.path.split(waiting_file)[1]
            combinePdf(waiting_file, outputfile, duplexfile)
            waiting_file = None
            

def ocrFile(input_file, output_file):
    try:
        ocrmypdf.ocr(input_file, output_file, 
            optimize=1,
            deskew=True,
            tesseract_timeout=400,
            skip_text=True, 
            max_image_mpixels=901167396,
            language=OCR_LANG
        )
        logger.info(f"Scan ocr'd: '{output_file}'")
        return True
    except:
        logger.error(f"Error: '{input_file}' could not be ocr'd by ocrmypdf!")
        return False
    finally:
        try:
            os.remove(input_file)
        except OSError:
            pass

def combinePdf(input_file_odd, input_file_even, output_file):
    #https://gist.github.com/bskinn/6f1b769d9ca0338c5056c6878c70be62
    try:
        pdf_out = pypdf.PdfWriter()

        with open(input_file_odd, 'rb') as f_odd:
            with open(input_file_even, 'rb')  as f_even:
                pdf_odd = pypdf.PdfReader(f_odd)
                pdf_even = pypdf.PdfReader(f_even)

                for p in itt.chain.from_iterable(
                    itt.zip_longest(
                        pdf_odd.pages,
                        reversed(pdf_even.pages),
                    )
                ):
                    if p:
                        pdf_out.add_page(p)

                with open(output_file, 'wb') as f_out:
                    pdf_out.write(f_out)
        logger.info(f"Scan's combined: '{output_file}'")
    except:
        logger.error(f"Error: '{input_file_odd}' and '{input_file_even}' could not be combined!")
    finally:
        try:
            os.remove(input_file_odd)
        except OSError:
            logger.error(f"Error: '{input_file_odd}' could not be deleted!")
        try:
            os.remove(input_file_even)
        except OSError:
            logger.error(f"Error: '{input_file_even}' could not be deleted!")

def main():
    if (OCR_LANG != "deu" and OCR_LANG != "eng"):
        try:
            subprocess.run(["apk", "add", "--update", "--no-cache", "tesseract-ocr-data-" + OCR_LANG])
        except:
            logger.error("Error downloading tesseract language data")
    try:
        logger.info("Checking tesseract langs so first run succeeds:")
        subprocess.run(["tesseract", "--list-langs"]) #must be called or first run will fail
    except:
        pass
    patterns = ["*.pdf"]
    ignore_patterns = None
    ignore_directories = False
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

    my_event_handler.on_created = on_pdf_created

    go_recursively = True
    my_observer = PollingObserver()
    my_observer.schedule(my_event_handler, CONSUME_FOLDER, recursive=go_recursively)

    Path(CONSUME_FOLDER).mkdir(mode=666, parents=True, exist_ok=True)
    Path(EXPORT_FOLDER).mkdir(mode=666, parents=True, exist_ok=True)

    global waiting_folder
    waiting_folder = tempfile.mkdtemp() + "/"
    
    my_observer.start()
    logger.info("Started observing " + CONSUME_FOLDER)
    try:
        while True:
            my_observer.join(1)
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()
    finally:
        shutil.rmtree(waiting_folder)

if __name__ == "__main__":
    main()