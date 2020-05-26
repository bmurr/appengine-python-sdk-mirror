#!/usr/bin/env python

import logging
import re
import os
import xml.etree.ElementTree as ET
import shutil
import pathlib


from git import Repo
import tqdm
import urllib3

logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
logger.propagate = False

def split_namespaced_name(name):
    m = re.match('^(?P<xmlns>{[^}]+})(?P<tag>.*)', name)
    return m.groupdict()['xmlns'], m.groupdict()['tag']

def get_all_versions(listings_url):
    http = urllib3.PoolManager()
    r = http.request('GET', listings_url)
    xml_data = r.data 
    
    root = ET.fromstring(xml_data)
    xmlns, tag = split_namespaced_name(root.tag)

    versions = []
    for contents in root.iter(f'{xmlns}Contents'):
        key, last_modified = None, None
        for child in contents:        
            if child.tag.endswith('Key'):
                key = child.text
            if child.tag.endswith('LastModified'):
                last_modified = child.text
        versions.append((key, last_modified))

    return versions

def download_zips(to_download, base_url, output_directory):    
    logger.info(f"Downloading latest {len(to_download)} versions.")
    shutil.rmtree(output_directory, ignore_errors=True)
    os.mkdir(output_directory)

    http = urllib3.PoolManager()
    for sdk_path, last_modified in tqdm.tqdm(to_download, ncols=100):        
        url = f'{base_url}{sdk_path}'
        filename = os.path.basename(sdk_path)
        output_filepath = os.path.join(output_directory, filename)
        with http.request('GET', url, preload_content=False) as r, open(output_filepath, 'wb') as out_file:       
            shutil.copyfileobj(r, out_file)


if __name__ == "__main__":

    # ./mirror_repo.py --git-credentials="/path/to/credentials" --update mirror
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--show",
        help="Show the available versions.",
        action='store_true',
        required=False,
    )

    parser.add_argument(
        "mirror",
        help="Show the available versions.",
        action='store_true',
    )

    parser.add_argument(
        "--git-credentials",
        help="Path to git credentials for remote repository.",
        required=False,
    )
    args = parser.parse_args()

    DIRECTORY_LISTING_URL = 'https://storage.googleapis.com/appengine-sdks?prefix=featured/google_appengine&marker=featured'
    BASE_DOWNLOAD_URL = 'https://storage.googleapis.com/appengine-sdks/featured/'
    OUTPUT_DIRECTORY_NAME = 'zips'
    OUTPUT_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), OUTPUT_DIRECTORY_NAME))
    LIMIT = 2

    # versions = get_all_versions(DIRECTORY_LISTING_URL)

    # if args.show:        
    #     for path, last_modified in versions:
    #         print(f'{BASE_DOWNLOAD_URL}{path}\t\t{last_modified}')
    #     exit()


    # to_download = versions[-LIMIT:]
    # download_zips(to_download, BASE_DOWNLOAD_URL, OUTPUT_DIRECTORY)
    # for sdk_path, last_modified in to_download:
    #     pass

    print Repo
    

   
    