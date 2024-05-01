#!/usr/bin/env python3

# requirement actions:
#   1. pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
#   2. pip3 install --upgrade oauth2client
#   3. setup profile in "OAuth consent screen" (https://console.cloud.google.com/apis/credentials/consent)
#       - User Type: External
#   4. add myself to "Test users" (https://console.cloud.google.com/apis/credentials/consent)
#       - User Info: jcnlcxc.new@gmail.com
#   5. create a credential in "OAuth 2.0 Client IDs" (https://console.cloud.google.com/apis/credentials)
#       - click "Create Credentials" -> "OAuth client ID"
#       - Application type: Desktop app
#   6. download the credential file and save it to "client_secrets_desktop.json"
#   7. enable "YouTube Data API v3" (https://console.cloud.google.com/apis/library/youtube.googleapis.com)
#
# critical api:
#   - https://developers.google.com/youtube/v3/docs/search/list
#   - https://developers.google.com/youtube/v3/docs/videos/list
#
# reference:
#   - https://github.com/tokland/youtube-upload#setup
#   - https://developers.google.com/youtube/v3/guides/uploading_a_video
#   - https://developers.google.com/youtube/v3/guides/implementation/videos#videos-upload
#   - https://github.com/tokland/youtube-upload/blob/master/youtube_upload/main.py
#
# Uploaded files must conform to these constraints:
#   - Maximum file size: 256GB
#   - Accepted Media MIME types: video/*, application/octet-stream

import os
import sys

# ================================================================
# WARNING: all the import sentenses below cannot be removed
# section start

import apiclient
import googleapiclient
import httplib2
import oauth2client
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

# section end
# ================================================================

SECRET_DIR = "/Users/cuixiaochen/GoogleDrive/clutter/secret"
CLIENT_SECRETS_FILE = os.path.join(SECRET_DIR, "client_secrets_desktop.json")
CREDENTIALS_FILE = os.path.join(SECRET_DIR, "youtube-credentials.json")

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_MANEUVER_SCOPE = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def console_get_code(authorize_url):
    """Show authorization URL and return the code the user wrote."""
    message = "Check this link in your browser: {0}".format(authorize_url)
    sys.stderr.write(message + "\n")
    return input("Enter verification code: ")


def get_credentials(flow, storage):
    """Return the user credentials. If not found, run the interactive flow."""
    existing_credentials = storage.get()
    if existing_credentials and not existing_credentials.invalid:
        return existing_credentials
    else:
        """Return the credentials asking the user."""
        flow.redirect_uri = oauth2client.client.OOB_CALLBACK_URN
        authorize_url = flow.step1_get_authorize_url()
        code = console_get_code(authorize_url)
        if code:
            credential = flow.step2_exchange(code, http=None)
            storage.put(credential)
            credential.set_store(storage)
            return credential


def get_resource():
    """Authenticate and return a googleapiclient.discovery.Resource object."""
    flow = oauth2client.client.flow_from_clientsecrets(
        CLIENT_SECRETS_FILE,
        scope=YOUTUBE_MANEUVER_SCOPE,
    )

    storage = oauth2client.file.Storage(CREDENTIALS_FILE)
    credentials = get_credentials(flow, storage)
    if credentials:
        httplib = httplib2.Http()
        httplib.redirect_codes = httplib.redirect_codes - {308}
        http = credentials.authorize(httplib)
        return googleapiclient.discovery.build("youtube", "v3", http=http)
