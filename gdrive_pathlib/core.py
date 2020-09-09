import json
import os
from pathlib import Path
import enum
import typing
from typing import List, Tuple
import functools

#ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build, Resource as GoogleResource

class GoogleMimeTypes(enum.Enum):
    Folder='application/vnd.google-apps.folder'
    SpreadSheet='application/vnd.google-apps.spreadsheet'
    Document='application/vnd.google-apps.document'

# basic api
class GoogleBasePath:
    def __init__(self, drive_service: GoogleResource):
        self.__drive_service

    @property
    def drive_service(self):
        return self.__drive_service

    def glob(self, id, file_fields: List[str]):
        page_token = None
        while True:
            response = drive_service.files().list(
                    q=f"'{self.id}' in parents",          # 親のIDを指定==ディレクトリを指定
                    spaces='drive',                         # drive
                    fields=f'nextPageToken, files({", ".join(file_fields)})',
                    pageToken=page_token
                ).execute()

            for file in response.get('files', []):
                yield file
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
    
    def rglob(self, id, file_fields: List[str]):
        for gp in self.glob(x):
            yield gp
            if gp.is_dir():
                yield from gp.glob(x)
    
    def __mkxxx(self, name, parent_id, mimeType):
        file_metadata = {
            'name': name,
            'mimeType': mimeType,
            'parents': [parent_id]
        }
        file = drive_service.files().create(
            body=file_metadata,
        ).execute()
        return file["id"]
    
    mkdir = functools.partial(self.__mkxxx, mimeType=GoogleMimeTypes.Folder)
    mksheet = functools.partial(self.__mkxxx, mimeType=GoogleMimeTypes.SpreadSheet)
    mkdocument = functools.partial(self.__mkxxx, mimeType=GoogleMimeTypes.Document)
