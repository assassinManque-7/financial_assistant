from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from services.gemma import ask_gemma

from services.doc_reader import read_doc

from services.gemma import ask_gemma

from fastapi.middleware.cors import CORSMiddleware

from services.onboarding_models import strip_quotes, parse_gemma_op

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
async def upload_pdf(file : UploadFile = File(...)):

    if file.content_type != "application/pdf":
        raise HTTPException(status_code = 400, detail = "File not PDF")

    file.file.seek(0)

    doc_dict = read_doc(file)

    gemma_output = ask_gemma(doc_dict["text"])

    stripped_resp = strip_quotes(gemma_output)

    try:
        validation_op = parse_gemma_op(stripped_resp, "business")
        return validation_op

    except ValueError as e:
        raise HTTPException(status_code = 422, detail = str(e)) #should be str(e) - e alone is a ValueError Objecta

    


    

    

