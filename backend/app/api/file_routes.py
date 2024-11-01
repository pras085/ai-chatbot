from pprint import pprint
from typing import List

from fastapi import APIRouter, UploadFile, File
from zipfile import ZipFile

from app.utils.docx_utils import extract_text_from_docx

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


@file_routes.post("/documents")
async def upload_documents(
    files: List[UploadFile] = File(...),  # Banyak file
):
    # Ekstrak teks from docx
    text_content = extract_text_from_docx(files[0].file)
    print(text_content)

