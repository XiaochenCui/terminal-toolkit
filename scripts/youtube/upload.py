#!/usr/bin/env python3
import http.client
import os
import pathlib
import time
from datetime import datetime

import apiclient
import common
import googleapiclient
import httplib2

UPLOAD_QUEUE_DIR = "/Volumes/CUI-2024/life_videos/upload_queue"
UPLOAD_SUCCESS_DIR = "/Volumes/CUI-2024/life_videos/uploaded"

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
# 403: Access denied. (The request cannot be completed because you have exceeded your <a href="/youtube/v3/getting-started#quota">quota</a>.)
ACCESS_DENIED_CODES = [403]


# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (
    httplib2.HttpLib2Error,
    IOError,
    http.client.NotConnected,
    http.client.IncompleteRead,
    http.client.ImproperConnectionState,
    http.client.CannotSendRequest,
    http.client.CannotSendHeader,
    http.client.ResponseNotReady,
    http.client.BadStatusLine,
)

upload_log = open("/tmp/upload.log", "w+")


def log(*values: object):
    print("{} | {}".format(datetime.now(), *values), flush=True)
    print("{} | {}".format(datetime.now(), *values), flush=True, file=upload_log)


# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request):
    response = None
    error = None
    log("Uploading file...")
    while response is None:
        try:
            status, response = insert_request.next_chunk()
            if response is not None:
                if "id" in response:
                    log(
                        (
                            "Video id '{}' was successfully uploaded.".format(
                                response["id"]
                            )
                        )
                    )
                else:
                    exit("The upload failed with an unexpected response: %s" % response)
        except googleapiclient.errors.HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (
                    e.resp.status,
                    e.content,
                )
                log(error)
                time.sleep(3)
            elif e.resp.status in ACCESS_DENIED_CODES:
                error = "ACCESS DENIED HTTP error %d occurred:\n%s" % (
                    e.resp.status,
                    e.content,
                )
                log(error)
                time.sleep(60 * 60)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e
            log(error)
            time.sleep(3)


def upload(full_path: str):
    filename = pathlib.Path(full_path).name

    log(("Uploading {0}".format(filename)))
    body = {
        "snippet": {
            "title": filename,
            "description": "recording my life",
            "categoryId": "22",
        },
        "status": {
            "privacyStatus": "private",
        },
    }
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=apiclient.http.MediaFileUpload(
            filename=full_path, chunksize=1024 * 1024, resumable=True
        ),
    )
    resumable_upload(request)
    log(("Uploaded {0}".format(filename)))


def is_video_file(filepath: str) -> bool:
    if not os.path.isfile(filepath):
        return False
    _, file_extension = os.path.splitext(filepath)
    return file_extension in [".mp4", ".mov", ".MP4", ".MOV"]


if __name__ == "__main__":
    youtube = common.get_resource()
    if youtube:
        files = os.listdir(UPLOAD_QUEUE_DIR)
        video_files = []
        for i, filename in enumerate(files):
            # remove invalid files by prefix
            if filename.startswith("."):
                continue

            full_path = os.path.join(UPLOAD_QUEUE_DIR, filename)
            if is_video_file(full_path):
                video_files.append(full_path)
        video_files.sort(key=lambda x: os.path.getmtime(x))

        log(("found {} video files".format(len(video_files))))

        for i, full_path in enumerate(video_files):
            filename = pathlib.Path(full_path).name

            upload(full_path)

            os.rename(
                os.path.join(UPLOAD_QUEUE_DIR, filename),
                os.path.join(UPLOAD_SUCCESS_DIR, filename),
            )
    else:
        raise Exception("Cannot get youtube resource")
