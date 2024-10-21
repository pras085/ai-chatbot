from pprint import pprint
from typing import List

from fastapi import APIRouter, UploadFile, File
from zipfile import ZipFile

file_routes = APIRouter()


@file_routes.post("/")
async def upload_files(
    files: List[UploadFile] = File(...),  # Banyak file
):
    file_contents = []

    # unzip file
    with ZipFile(files[0].file, 'r') as zipObj:
        # Extract all the contents of zip file in current directory
        zipObj.extractall(path="uploads")

        for file in zipObj.namelist():
            # seek 0
            content = zipObj.read(file)
            file_contents.append(
                {
                    "name": file,
                    "content": content.decode("utf-8", errors="ignore"),
                }
            )

    # print all the file names
    files = zipObj.namelist()

    print(files)
    pprint(file_contents)
