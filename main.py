import os
import zipfile

from parse import write_to_csv, multiprocessed_parsing
from generate import create_zip
from consts import NUMBER_OF_ZIPS, ROOT_PATH, ZIP_DIR, LEVELS_CSV_NAME, OBJECTS_CSV_NAME

from log import logger

if __name__ == "__main__":

    for i in range(NUMBER_OF_ZIPS):
        zipname = str(i) + ".zip"
        create_zip(zipname)
    all_zips = []
    for zipname in os.listdir(os.path.join(ROOT_PATH, ZIP_DIR)):
        if zipname.endswith(".zip"):
            all_zips.append(os.path.join(ROOT_PATH, ZIP_DIR, zipname))

    results = multiprocessed_parsing(all_zips)

    if os.path.isfile(LEVELS_CSV_NAME):
        os.remove(LEVELS_CSV_NAME)

    if os.path.isfile(OBJECTS_CSV_NAME):
        os.remove(OBJECTS_CSV_NAME)

    for result in results:
        write_to_csv(LEVELS_CSV_NAME, result["levels"])
        write_to_csv(OBJECTS_CSV_NAME, result["objects"])
