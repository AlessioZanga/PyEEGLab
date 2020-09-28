import logging
import subprocess


def wget(path: str, user: str, password: str, slug: str, version: str) -> None:
    logging.info("Download started, it will take some time")
    url = "https://physionet.org/files/" + slug + "/" + version + "/"
    process = subprocess.Popen(
        [
            "wget",
            "-r",
            "-N",
            "-c",
            "-np",
            "-nH",
            "--cut-dirs=3",
            url,
            "-P",
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
