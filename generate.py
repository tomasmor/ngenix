import uuid
import random
import string
import os
import zipfile
import tempfile

import xml.etree.ElementTree as ET
import lxml.etree as etree

from consts import ROOT_PATH, ZIP_DIR, NUMBER_XMLS_IN_FOLDER

def random_string(lenght):
    return "".join(random.choice(string.uppercase + string.lowercase) for i in range(lenght))

def add_objects(xml):
    number_of_objects = random.randint(1, 10)
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
    zip_folder_path = os.path.join(tempfile.gettempdir(), ZIP_DIR)
    if not os.path.exists(zip_folder_path):
        os.mkdir(zip_folder_path)
    path = os.path.join(zip_folder_path, zipname)

    with zipfile.ZipFile(path, "w") as zipfilefhandler:
        for i in range(NUMBER_XMLS_IN_FOLDER):
            filename = str(i) + ".xml"
            xml = create_xml()
            zipfilefhandler.writestr(filename, xml)
    return zip_folder_path
