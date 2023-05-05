#!/usr/bin/env python
from dataclasses import dataclass
import datetime
import logging
import json
import re
import os
import xml.etree.ElementTree as ET
import shutil
import tarfile
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


@dataclass
class ComponentInfo:
    url: str
    version: str
    build_number: int
    filename: int

    @property
    def last_modified(self):
        return datetime.datetime.strptime(str(self.build_number), "%Y%m%d%H%M%S")


class GoogleCloudSDKDownloader:
    @staticmethod
    def get_gcloud_versions(release_notes_url):
        logger.info("Checking for latest version...")
        http = urllib3.PoolManager()
        r = http.request("GET", release_notes_url)
        release_notes = r.data.decode("utf-8")
        versions = re.findall(
            r"##\s+(\d+.\d+.\d+)\s+\(\d{4}\-\d{2}\-\d{2}\)", release_notes
        )
        return versions

    @staticmethod
    def get_component_info(component_name, gcloud_versions):
        logger.info(
            f"Fetching component info for {len(gcloud_versions)} Cloud SDK versions."
        )
        http = urllib3.PoolManager()
        version_components = {}

        for version in tqdm.tqdm(gcloud_versions, ncols=100):
            version_url = GCLOUD_COMPONENTS_URL.format(version=version)
            r = http.request("GET", version_url)

            version_components[version] = {}
            component_info = {}
            try:
                components = json.loads(r.data)
                component_info = [
                    dict(
                        [
                            ("version_string", c["version"]["version_string"]),
                            ("build_number", c["version"]["build_number"]),
                            ("source", c["data"]["source"]),
                        ]
                    )
                    for c in components["components"]
                    if c["id"] == "app-engine-python"
                ][0]
                version_components[version][component_name] = component_info
            except:
                pass

        return version_components

    @staticmethod
    def get_local_info(component_name):

        try:
            with open(VERSION_INFO_PATH, encoding="utf-8") as f:
                return json.load(f)
        except:
            logger.info(f"Could not load local version info.")
            return {}

    @staticmethod
    def get_version_json(*args):
        gcloud_versions = GoogleCloudSDKDownloader.get_gcloud_versions(
            RELEASE_NOTES_URL
        )

        info = GoogleCloudSDKDownloader.get_local_info("app-engine-python-sdk")
        remote_versions = [k for k in gcloud_versions if not k in info]

        if remote_versions:
            component_infos = GoogleCloudSDKDownloader.get_component_info(
                "app-engine-python-sdk", remote_versions
            )
            info.update(component_infos)

            with open(VERSION_INFO_PATH, "wb") as f:
                f.write(json.dumps(info, indent=4).encode("utf-8"))

        return info

    @staticmethod
    def get_all_versions(*args):
        info = GoogleCloudSDKDownloader.get_version_json()
        versions = []
        for cloud_sdk, version_components in info.items():
            component = version_components.get("app-engine-python-sdk")

            if not component:
                continue

            version_string = component["version_string"]
            build_number = component["build_number"]
            source = component["source"]

            download_url = f"{GCLOUD_BASE_DOWNLOAD_URL}{source}"
            component_info = ComponentInfo(
                download_url,
                version_string,
                build_number,
                f"app-engine-python-sdk_{version_string}.tar.gz",
            )
            versions.append((version_string, component_info))
            
        versions = sorted(versions, key=lambda p: p[1].build_number, reverse=True)
        return dict(versions)

    @staticmethod
    def list_versions(versions, args):
        for version_string, info in versions.items():
            print(f"{info.filename}\t\t{info.last_modified}")

    @staticmethod
    def download_zips(to_download, output_directory):
        logger.info(f"Downloading latest {len(to_download)} versions.")
        shutil.rmtree(output_directory, ignore_errors=True)
        os.mkdir(output_directory)

        http = urllib3.PoolManager()
        for version_number, item in tqdm.tqdm(to_download, ncols=100):
            filename = item.filename
            output_filepath = os.path.join(output_directory, filename)
            with http.request("GET", item.url, preload_content=False) as r, open(
                output_filepath, "wb"
            ) as out_file:
                shutil.copyfileobj(r, out_file)

    @staticmethod
    def download(versions, args):
        to_download = (
            list(versions.items())[: args.limit]
            if (args.limit is not None and not args.all)
            else versions
        )

        GoogleCloudSDKDownloader.download_zips(to_download, ZIP_OUTPUT_DIRECTORY)
        exit(f"{len(to_download)} archives downloaded to {ZIP_OUTPUT_DIRECTORY}")

    @staticmethod
    def update(versions, args):
        latest_version = get_latest_version_from_commits(THIS_DIRECTORY)
        to_download = list(versions.items())

        if latest_version:
            for i, (version_num, info) in enumerate(versions.items()):
                if version_num.endswith(f"{latest_version}"):
                    to_download = list(reversed(to_download[:i]))
                    break

            logger.info(f"Latest version is {latest_version}.")
            if i == 0:
                exit("Repo is already up to date.")
        else:
            to_download = list(reversed(to_download))
            logger.info(f"No latest version found.")

        logger.info(f"Will update the repo with {len(to_download)} new versions.")

        if not args.no_download:
            GoogleCloudSDKDownloader.download_zips(to_download, ZIP_OUTPUT_DIRECTORY)

        for version_number, item in to_download:
            zip_filename = os.path.join(ZIP_OUTPUT_DIRECTORY, item.filename)
            try:
                extract_tar_files(zip_filename, None)
            except Exception as e:
                raise
                logger.error(f"Could not open {zip_filename}, skipping.")

            commit_date = item.last_modified.strftime("%d-%b-%Y")
            commit_message = (
                f"""{commit_date} Google AppEngine Python SDK v{version_number}"""
            )
            commit_files(
                THIS_DIRECTORY,
                commit_message,
                files_to_commit=["google_appengine*"],
                author_date=item.last_modified.isoformat(timespec="seconds"),
                commit_date=item.last_modified.isoformat(timespec="seconds"),
            )


def extract_zip_files(zip_filename, output_directory=None):
    logger.info(f"Extracting {zip_filename}")
    with zipfile.ZipFile(zip_filename, "r") as _zip:
        _zip.extractall(path=output_directory)


def extract_tar_files(tar_filename, output_directory=None):
    logger.info(f"Extracting {tar_filename}")
    output_directory = output_directory or "."

    def members(tf):
        l = len("platform/")
        for member in tf.getmembers():
            if member.path.startswith("platform/"):
                member.path = member.path[l:]
                yield member

    with tarfile.open(tar_filename, "r:gz") as _tar:
        def is_within_directory(directory, target):

            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)

            prefix = os.path.commonprefix([abs_directory, abs_target])

            return prefix == abs_directory

        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):

            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")

            tar.extractall(path, members, numeric_owner=numeric_owner) 


        safe_extract(_tar, path=output_directory, members=members(_tar))


def commit_files(
    repository_directory,
    commit_message,
    files_to_commit=None,
    author_date=None,
    commit_date=None,
):
    logger.info(f'Committing "{commit_message}"')
    repo = git.Repo(repository_directory)
    if files_to_commit:
        repo.git.add([files_to_commit])
    else:
        repo.git.add("--all")

    author = git.Actor("Google", "appengine@google.com")
    repo.index.commit(
        commit_message, author=author, author_date=author_date, commit_date=commit_date
    )


def get_latest_version_from_commits(repository_directory):
    repo = git.Repo(repository_directory)
    for c in repo.iter_commits("master"):
        m = re.match(
            r"\d{2}-\w{3}-\d{4} Google AppEngine Python SDK v(?P<version>\d+.\d+.\d+)",
            c.message,
        )
        if m:
            return m.groupdict()["version"]


if __name__ == "__main__":
    import argparse

    downloader = GoogleCloudSDKDownloader

    parser = argparse.ArgumentParser(
        description="""Tool to create a git repo of the Google App Engine Python SDK"""
    )

    subparsers = parser.add_subparsers(
        title="Actions", dest="{list, download, update, generate}"
    )
    subparsers.required = True

    parser_list = subparsers.add_parser(
        "list", help="Check the available SDK versions and print them."
    )
    parser_list.set_defaults(func=downloader.list_versions)

    parser_generate = subparsers.add_parser(
        "generate", help="Generate helper JSON with stored version and location info."
    )
    parser_generate.set_defaults(func=downloader.get_version_json)

    parser_download = subparsers.add_parser(
        "download", help="Download the available versions, but do not commit them."
    )
    download_options = parser_download.add_mutually_exclusive_group(required=True)

    download_options.add_argument(
        "--limit",
        help="Limit to downloading the last <limit> available versions.",
        type=int,
    )
    download_options.add_argument(
        "--all", action="store_true", help="Download all the available versions."
    )
    parser_download.set_defaults(func=downloader.download)

    parser_update = subparsers.add_parser(
        "update",
        help="Fetch and commit any new versions since the last commited version.",
    )
    parser_update.add_argument(
        "--no_download",
        action="store_true",
        help="Assume the archives already exist in the default download path.",
    )
    parser_update.set_defaults(func=downloader.update)

    THIS_DIRECTORY = os.path.dirname(__file__)
    DIRECTORY_LISTING_URL = "https://storage.googleapis.com/appengine-sdks?prefix=featured/google_appengine&marker=featured"
    LEGACY_BASE_DOWNLOAD_URL = "https://storage.googleapis.com/appengine-sdks/"

    RELEASE_NOTES_URL = "https://dl.google.com/dl/cloudsdk/channels/rapid/RELEASE_NOTES"
    GCLOUD_BASE_DOWNLOAD_URL = "https://dl.google.com/dl/cloudsdk/channels/rapid/"
    GCLOUD_COMPONENTS_URL = (
        "https://dl.google.com/dl/cloudsdk/channels/rapid/components-v{version}.json"
    )

    VERSION_INFO_PATH = "cloudsdk_component_info.json"

    ZIP_DIRECTORY_NAME = "zips"
    CODE_DIRECTORY_NAME = "google_appengine"
    ZIP_OUTPUT_DIRECTORY = os.path.abspath(
        os.path.join(THIS_DIRECTORY, ZIP_DIRECTORY_NAME)
    )

    versions = downloader.get_all_versions()

    args = parser.parse_args()
    args.func(versions, args)
