from fastapi import FastAPI, UploadFile, File, HTTPException
from services.gemma import ask_gemma

from services.doc_reader import read_doc

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

from pydantic import BaseModel

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5173"],
    allow_credentials = True,
    allow_methods = ["*"], 
    allow_headers = ["*"],
)

@app.post("/read_pdf")
async def upload_pdf(file : UploadFile = File(...) ):

    if file.content_type != "application/pdf":
        raise HTTPException(status_code = 400, detail = "File not PDF")

    file.file.seek(0)

    doc_dict = read_doc(file)

    return doc_dict

