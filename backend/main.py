from fastapi import FastAPI
from services.gemma import ask_gemma

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

from pydantic import BaseModel

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5174"],
    allow_credentials = True,
    allow_methods = ["*"], 
    allow_headers = ["*"],
)

class Input(BaseModel):
    docs : str

@app.post("/analyze")
def send_gem(inp : Input):
    response = ask_gemma(inp.docs)
    return {
        "response" : response
    }


