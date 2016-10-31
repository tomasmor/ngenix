import xml.etree.ElementTree as ET
import lxml.etree as etree
import uuid
import random
import string
import os
import zipfile
import logging
import multiprocessing
import csv

from contextlib import closing

logging.basicConfig(filename="log.txt", level=logging.DEBUG)
logger = logging.getLogger(__name__)

NUMBER_XMLS_IN_FOLDER = 100
NUMBER_OF_ZIPS = 50

ROOT_PATH = os.path.abspath(os.curdir)
ZIP_DIR = "zips"

LEVELS_CSV_NAME = "levels.csv"
OBJECTS_CSV_NAME = "objects.csv"


def random_string(len):
    return "".join(random.choice(string.uppercase + string.lowercase)
    for i in range(len))

def add_objects(xml):
    number_of_objects = random.randint(1,10)
    objects = ET.SubElement(xml, "objects")
    for i in range(number_of_objects):
        obj = ET.SubElement(objects, "object")
        obj.attrib["name"] = random_string(10)

def create_xml():
    root = ET.Element("root")
    var = ET.SubElement(root, "var")
    var.attrib["name"] = "id"
    var.attrib["value"] = uuid.uuid4().hex

    var = ET.SubElement(root, "var")
    var.attrib["name"] = "level"
    var.attrib["value"] = str(random.randint(1, 100))
    add_objects(root)
    return ET.tostring(root, "utf-8")

def create_zip(zipname):
    path = os.path.join(ROOT_PATH, ZIP_DIR, zipname)

    with zipfile.ZipFile(path, "w") as zf:
        for i in range(NUMBER_XMLS_IN_FOLDER):
            filename = str(i) + ".xml"
            xml = create_xml()
            zf.writestr(filename, xml)

def parse_xml(xml):
    tree = ET.fromstring(xml)
    unique_name = tree.findall("./var[@name='id']")
    level = tree.findall("./var[@name='level']")
    if len(unique_name) > 1 or len(level) > 1:
        logger.warning("XML was created unconsistent")
    objects_elements = tree.findall("./objects/object")
    objects = []
    for obj in objects_elements:
        objects.append(obj.attrib["name"])
    result =  {"id":unique_name[0].attrib["value"], "level":level[0].attrib["value"], "objects":objects}
    return result

def extract_xml(path_to_zip):
    result = {"levels":[], "objects":[]}
    with zipfile.ZipFile(path_to_zip, "r") as zf:
        file_list = zf.namelist()
        for f in file_list:
            with zf.open(f, "r") as xml:
                parsed_data = parse_xml(xml.read())
                result["levels"].append(parsed_data["id"] +" "+ parsed_data["level"])
                for obj in parsed_data["objects"]:
                    result["objects"].append(parsed_data["id"] +" "+ obj)
    return result

def write_to_csv(csv_path, data):

    with open(csv_path, "ab") as csvf:

        writer = csv.writer(csvf, delimiter=' ', quoting=csv.QUOTE_NONE, escapechar="|")
        writer.writerows(data)

if __name__ == "__main__":

    for i in range(NUMBER_OF_ZIPS):
        zipname = str(i) + ".zip"
        create_zip(zipname)

    all_zips = []
    extracted_data = []
    for zipname in os.listdir(os.path.join(ROOT_PATH, ZIP_DIR)):
        if zipname.endswith(".zip"):
            all_zips.append(os.path.join(ROOT_PATH, ZIP_DIR, zipname))

    with closing(multiprocessing.Pool(processes=2)) as pool:
        results = pool.map(extract_xml, all_zips, chunksize=1)
        pool.terminate()

    if os.path.isfile(LEVELS_CSV_NAME):
        os.remove(LEVELS_CSV_NAME)

    if os.path.isfile(OBJECTS_CSV_NAME):
        os.remove(OBJECTS_CSV_NAME)

    for result in results:
        write_to_csv(LEVELS_CSV_NAME, result["levels"])
        write_to_csv(OBJECTS_CSV_NAME, result["objects"])
