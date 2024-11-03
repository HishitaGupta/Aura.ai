from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import os
from testmain import *
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import json

app = FastAPI() 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def home():
    return {"message": "Home route"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # Check if the file is a PDF
    if file.content_type != "application/pdf":
        return {"error": "File is not a PDF"}

    temp_file_path = f"temp_{file.filename}"

    # Write the uploaded file to the temporary file
    with open(temp_file_path, "wb") as f:
        f.write(await file.read())


