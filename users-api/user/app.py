import boto3
import json
import base64
import os
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all 
from apiclient import errors
import httplib2
from apiclient import discovery
from oauth2client import client
from oauth2client.service_account import ServiceAccountCredentials

# Patch all supported libraries for X-Ray - More info: https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-python-patching.html
patch_all()

session = boto3.Session(region_name="eu-west-1")

kms = session.client('kms')

SCOPES = ['https://www.googleapis.com/auth/admin.directory.user.readonly',
          'https://www.googleapis.com/auth/admin.directory.group.readonly']

# KMS encrypted client_secret.json
CLIENT_SECRET = os.environ.get('client_secret')

credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(
        kms.decrypt(CiphertextBlob=base64.b64decode(CLIENT_SECRET))
        .get('Plaintext')
        .decode()
    ), SCOPES
)

credentials = credentials.create_delegated("ian@ianduffy.ie")

http = credentials.authorize(httplib2.Http(cache="/tmp/.cache"))
service = discovery.build('admin', 'directory_v1', http=http)

def lambda_handler(event, context):
    try:
        gapps_user = service.users().get(
            userKey=event['pathParameters']['uid'],
            viewType="admin_view",
            projection="full"
        ).execute()

        gapps_user_groups = service.groups().list(
            domain="ianduffy.ie",
            userKey=event['pathParameters']['uid']
        ).execute()

        print(json.dumps(gapps_user))

        user = {
            "id": gapps_user["id"],
            "email": gapps_user["primaryEmail"],
            "suspended": gapps_user["suspended"],
            "photo": gapps_user["thumbnailPhotoUrl"],
            "groups": [x['email'] for x in gapps_user_groups['groups']],
            "name": gapps_user["name"]["fullName"]
        }

        return {
            "statusCode": 200,
            "body": json.dumps(user)
        }
    except errors.HttpError as error:
        print(error._get_reason())
        return {
            "statusCode": error.resp.status
        }
