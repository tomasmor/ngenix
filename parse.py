import xml.etree.ElementTree as ET
import os
import zipfile
import csv
from contextlib import closing
import multiprocessing

from log import logger

def parse_xml(xml):
    tree = ET.fromstring(xml)
    unique_name = tree.findall("./var[@name='id']")
    level = tree.findall("./var[@name='level']")
    if len(unique_name) > 1 or len(level) > 1:
        logger.warning("XML was created unconsistent, id or level is not the one in it")
    objects_elements = tree.findall("./objects/object")
    objects = []
    for obj in objects_elements:
        objects.append(obj.attrib["name"])
    result =  {
        "id":unique_name[0].attrib["value"],
        "level":level[0].attrib["value"], "objects":objects
        }
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
        writer = csv.writer(csvf, delimiter=' ',
                        quoting=csv.QUOTE_NONE, escapechar="|")
        writer.writerows(data)

def multiprocessed_parsing(all_zips):
    logger.info("Run extracting from xmls in two processes")
    with closing(multiprocessing.Pool(processes=2)) as pool:
        results = pool.map(extract_xml, all_zips, chunksize=1)
        pool.terminate()
        return results
