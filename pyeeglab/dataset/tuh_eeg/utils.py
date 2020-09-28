import re
import logging
import subprocess

from uuid import uuid4

from typing import List

from ..file import File
from ..annotation import Annotation


def rsync(path: str, user: str, password: str, slug: str, version: str) -> None:
    if user is not None and password is not None:
        logging.info("Download started, it will take some time")
        url = user + "@" + "www.isip.piconepress.com:~/data/"
        url = url + slug + "/v" + version + "/"
        process = subprocess.Popen(
            [
                "sshpass",
                "-p",
                password,
                "rsync",
                "-auxvL",
                url,
                path
            ],
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
        while True:
            output = process.stdout.readline()
            logging.info(output.strip())
            if process.poll() is not None:
                for output in process.stdout.readlines():
                    logging.info(output.strip())
                break
    else:
        logging.warn("Download disabled, add 'user' and 'password' as optional parameters during data set creation")
        logging.warn("Request your login credentials at: https://www.isip.piconepress.com/projects/tuh_eeg/html/request_access.php")


def parse_lbl(file: File) -> List[Annotation]:
    path = file.path[:-4] + ".lbl"
    with open(path, "r") as reader:
        annotations = reader.read()
    symbols = re.compile(
        r"^symbols\[0\] = ({.*})$",
        re.MULTILINE
    )
    symbols = re.findall(symbols, annotations)
    symbols = eval(symbols[0])
    pattern = re.compile(
        r"^label = {([^,]*), ([^,]*), ([^,]*), ([^,]*), ([^,]*), ([^}]*)}$",
        re.MULTILINE
    )
    annotations = re.findall(pattern, annotations)
    annotations = {
        (annotation[2], annotation[3], symbols[index])
        for annotation in annotations
        for index, value in enumerate(eval(annotation[5]))
        if value > 0
    }
    annotations = [
        Annotation(
            uuid=str(uuid4()),
            file_uuid=file.uuid,
            begin=float(annotation[0]),
            end=float(annotation[1]),
            label=annotation[2]
        )
        for annotation in annotations
    ]
    return annotations


def parse_tse(file: File) -> List[Annotation]:
    path = file.path[:-4] + ".tse"
    with open(path, "r") as reader:
        annotations = reader.read()
    pattern = re.compile(
        r"^(\d+.\d+) (\d+.\d+) (\w+) (\d.\d+)$",
        re.MULTILINE
    )
    annotations = re.findall(pattern, annotations)
    annotations = [
        Annotation(
            uuid=str(uuid4()),
            file_uuid=file.uuid,
            begin=float(annotation[0]),
            end=float(annotation[1]),
            label=annotation[2]
        )
        for annotation in annotations
    ]
    return annotations
