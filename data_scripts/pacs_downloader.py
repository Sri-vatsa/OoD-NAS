from zipfile import ZipFile
import argparse
import tarfile
import shutil
import gdown
import uuid
import json
import os

from pathlib import Path

def stage_path(data_dir, name):
    full_path = os.path.join(data_dir, name)

    if not os.path.exists(full_path):
        os.makedirs(full_path)

    return full_path


def download_and_extract(url, dst, remove=True):
    gdown.download(url, dst, quiet=False)

    if dst.endswith(".tar.gz"):
        tar = tarfile.open(dst, "r:gz")
        tar.extractall(os.path.dirname(dst))
        tar.close()

    if dst.endswith(".tar"):
        tar = tarfile.open(dst, "r:")
        tar.extractall(os.path.dirname(dst))
        tar.close()

    if dst.endswith(".zip"):
        zf = ZipFile(dst, "r")
        zf.extractall(os.path.dirname(dst))
        zf.close()

    if remove:
        os.remove(dst)

def download_pacs(data_dir, path_to_data_scripts_folder):
    # Original URL: http://www.eecs.qmul.ac.uk/~dl307/project_iccv2017
    full_path = stage_path(data_dir, "PACS")

    download_and_extract(
        "https://drive.google.com/uc?id=1JFr8f805nMUelQWWmfnJR3y4_SYoN5Pd",
        os.path.join(data_dir, "PACS.zip"),
    )

    os.rename(os.path.join(data_dir, "kfold"), full_path)

    shutil.copytree(os.path.join(path_to_data_scripts_folder, "pacs_filepaths/"), os.path.join(full_path, 'kfold'))

data_root_directory = "./data/"

path_to_data_scripts_folder = "./NAS-OoD/data_scripts/"

#full_path = stage_path(data_root_directory, "PACS")

#shutil.copytree(os.path.join(path_to_data_scripts_folder, "pacs_filepaths/"), os.path.join(full_path, 'kfold'))

Path(data_root_directory).mkdir(parents=True, exist_ok=True)

download_pacs(data_root_directory, path_to_data_scripts_folder)