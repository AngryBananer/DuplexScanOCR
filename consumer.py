import os
import shutil
import tempfile
from pathlib import Path
import subprocess
import ocrmypdf
from watchdog.observers.polling import PollingObserver
from watchdog.events import PatternMatchingEventHandler

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        #logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

consume_folder = "/data/consume/" #input folder
export_folder = "/data/export/" #output folder

try:
    duplex_timeout = int(os.environ['DUPLEX_TIMEOUT'])
except:
    logging.warning("Could not get enviroment variable 'DUPLEX_TIMEOUT', setting timeout to 600")
    duplex_timeout = 600

waiting_folder = None
waiting_file = None

def on_created(event):
    inputfile= event.src_path
    logging.info(f"PDF-file '{inputfile}' has been created!")
    if "duplex" not in inputfile:
        logging.info("No duplex scan...")
        outputfile = export_folder + "ocr_" + os.path.split(inputfile)[1]
        ocrFile(inputfile, outputfile)
    else:
        logging.info("Duplex scan!")
        outputfile = waiting_folder + "ocr_" + os.path.split(inputfile)[1]
        if not ocrFile(inputfile, outputfile):
            return
        global waiting_file
        if waiting_file is None:
            waiting_file = outputfile
        elif duplex_timeout > 0 and os.path.getmtime(outputfile) - os.path.getmtime(waiting_file) > duplex_timeout:
            logging.warning(f"Waiting file '{waiting_file}' is older than {str(duplex_timeout)} seconds, deleting and waiting with current file.")
            try:
                os.remove(waiting_file)
            except OSError:
                pass
            waiting_file = outputfile
        else:
            logging.info("Combinig scans...")
            duplexfile = export_folder + os.path.split(waiting_file)[1]
            pdftk(waiting_file, outputfile, duplexfile)
            waiting_file = None
            

def ocrFile(input_file, output_file):
    try:
        ocrmypdf.ocr(input_file, output_file, 
            optimize=1,
            deskew=True,
            tesseract_timeout=400,
            skip_text=True, 
            max_image_mpixels=901167396,
            language="deu"
        )
        logging.info(f"Scan ocr'd: '{output_file}'")
        return True
    except:
        logging.error(f"Error: '{input_file}' could not be ocr'd by ocrmypdf!")
        return False
    finally:
        try:
            os.remove(input_file)
        except OSError:
            pass

def pdftk(input_file_odd, input_file_even, output_file):
    try:
        subprocess.run(["pdftk", "A=" + input_file_odd, "B=" + input_file_even, "shuffle", "A", "Bend-1", "output", output_file], capture_output=True)
        logging.info(f"Scan's combined: '{output_file}'")
    except:
        logging.error(f"Error: '{input_file_odd}' and '{input_file_even}' could not be combined!")
    finally:
        try:
            os.remove(input_file_odd)
            os.remove(input_file_even)
        except OSError:
            pass

def main():
    patterns = ["*.pdf"]
    ignore_patterns = None
    ignore_directories = False
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

    my_event_handler.on_created = on_created

    go_recursively = True
    my_observer = PollingObserver()
    my_observer.schedule(my_event_handler, consume_folder, recursive=go_recursively)

    Path(consume_folder).mkdir(exist_ok=True)
    Path(export_folder).mkdir(exist_ok=True)

    global waiting_folder
    waiting_folder = tempfile.mkdtemp() + "/"
    
    my_observer.start()
    logging.info("Started observing " + consume_folder)
    logging.debug("Duplex timeout set to " + str(duplex_timeout))
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