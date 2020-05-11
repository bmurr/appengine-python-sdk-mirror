#!/usr/bin/env python
import datetime
import logging
import re
import os
import xml.etree.ElementTree as ET
import shutil
import pathlib
import zipfile

import git
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
    m = re.match("^(?P<xmlns>{[^}]+})(?P<tag>.*)", name)
    return m.groupdict()["xmlns"], m.groupdict()["tag"]


def get_all_versions(listings_url):
    http = urllib3.PoolManager()
    r = http.request("GET", listings_url)
    xml_data = r.data

    root = ET.fromstring(xml_data)
    xmlns, tag = split_namespaced_name(root.tag)

    versions = []
    for contents in root.iter(f"{xmlns}Contents"):
        key, last_modified = None, None
        for child in contents:
            if child.tag.endswith("Key"):
                key = child.text
            if child.tag.endswith("LastModified"):
                last_modified = child.text
        versions.append((key, last_modified))

    return versions


def download_zips(to_download, base_url, output_directory):
    logger.info(f"Downloading latest {len(to_download)} versions.")
    shutil.rmtree(output_directory, ignore_errors=True)
    os.mkdir(output_directory)

    http = urllib3.PoolManager()
    for sdk_path, last_modified in tqdm.tqdm(to_download, ncols=100):
        url = f"{base_url}{sdk_path}"
        filename = os.path.basename(sdk_path)
        output_filepath = os.path.join(output_directory, filename)
        with http.request("GET", url, preload_content=False) as r, open(output_filepath, "wb") as out_file:
            shutil.copyfileobj(r, out_file)


def extract_files(zip_filename, output_directory=None):
    logger.info(f"Extracting {zip_filename}")
    with zipfile.ZipFile(zip_filename, "r") as _zip:
        _zip.extractall(path=output_directory)


def commit_files(repository_directory, commit_message, files_to_commit=None, author_date=None, commit_date=None):
    logger.info(f'Committing "{commit_message}"')
    repo = git.Repo(repository_directory)
    if files_to_commit:
        repo.git.add([files_to_commit])
    else:
        repo.git.add("--all")

    author = git.Actor("Google", "appengine@google.com")
    repo.index.commit(commit_message, author=author, author_date=author_date, commit_date=commit_date)


def get_latest_version_from_commits(repository_directory):
    repo = git.Repo(repository_directory)
    for c in repo.iter_commits("master"):
        m = re.match(r"\d{2}-\w{3}-\d{4} Google AppEngine Python SDK v(?P<version>\d+.\d+.\d+)", c.message,)
        if m:
            return m.groupdict()["version"]


def show(versions, args):
    for path, last_modified in versions:
        print(f"{BASE_DOWNLOAD_URL}{path}\t\t{last_modified}")


def download(versions, args):
    to_download = versions[-args.limit :] if (args.limit is not None and not args.all) else versions
    download_zips(to_download, BASE_DOWNLOAD_URL, ZIP_OUTPUT_DIRECTORY)
    exit(f"{len(to_download)} archives downloaded to {ZIP_OUTPUT_DIRECTORY}")


def update(versions, args):
    to_download = versions
    latest_version = get_latest_version_from_commits(THIS_DIRECTORY)

    if latest_version:
        for i, (sdk_path, last_modified) in enumerate(reversed(versions)):
            if sdk_path.endswith(f"{latest_version}.zip"):
                to_download = to_download[-i:]
                break

        logger.info(f"Latest version is {latest_version}.")
        if i == 0:
            exit("Repo is already up to date.")
    else:
        logger.info(f"No latest version found.")

    logger.info(f"Will update the repo with {len(to_download)} new versions.")

    if not args.no_download:
        download_zips(to_download, BASE_DOWNLOAD_URL, ZIP_OUTPUT_DIRECTORY)

    for sdk_path, last_modified in to_download:
        filename = os.path.basename(sdk_path)
        raw_filename, ext = os.path.splitext(filename)
        _, version = raw_filename.rsplit("_", 1)
        last_modified_date = datetime.datetime.strptime(last_modified, "%Y-%m-%dT%H:%M:%S.%fZ")

        zip_filename = os.path.join(ZIP_OUTPUT_DIRECTORY, filename)
        try:
            extract_files(zip_filename, None)
        except zipfile.BadZipFile:
            logger.error(f"Could not open {zip_filename}, skipping.")

        commit_date = last_modified_date.strftime("%d-%b-%Y")
        commit_message = f"""{commit_date} Google AppEngine Python SDK v{version}"""
        commit_files(
            THIS_DIRECTORY, commit_message, 
            files_to_commit=["google_appengine*"],
            author_date=last_modified_date.isoformat(timespec='seconds'),
            commit_date=last_modified_date.isoformat(timespec='seconds')
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="""Tool to create a git repo of the Google App Engine Python SDK""")

    subparsers = parser.add_subparsers(title="Actions", dest="{show, download, update}")
    subparsers.required = True

    parser_show = subparsers.add_parser("show", help="Check the available SDK versions and print them.")
    parser_show.set_defaults(func=show)

    parser_download = subparsers.add_parser("download", help="Download the available versions, but do not commit them.")
    download_options = parser_download.add_mutually_exclusive_group(required=True)

    download_options.add_argument(
        "--limit", help="Limit to downloading the last <limit> available versions.", type=int,
    )
    download_options.add_argument("--all", action="store_true", help="Download all the available versions.")
    parser_download.set_defaults(func=download)

    parser_update = subparsers.add_parser(
        "update", help="Fetch and commit any new versions since the last commited version.",
    )
    parser_update.add_argument("--no_download", action="store_true", help="Assume the archives already exist in the default download path.")
    parser_update.set_defaults(func=update)

    THIS_DIRECTORY = os.path.dirname(__file__)
    DIRECTORY_LISTING_URL = (
        "https://storage.googleapis.com/appengine-sdks?prefix=featured/google_appengine&marker=featured"
    )
    BASE_DOWNLOAD_URL = "https://storage.googleapis.com/appengine-sdks/"

    ZIP_DIRECTORY_NAME = "zips"
    CODE_DIRECTORY_NAME = "google_appengine"
    ZIP_OUTPUT_DIRECTORY = os.path.abspath(os.path.join(THIS_DIRECTORY, ZIP_DIRECTORY_NAME))

    versions = get_all_versions(DIRECTORY_LISTING_URL)

    args = parser.parse_args()
    args.func(versions, args)
