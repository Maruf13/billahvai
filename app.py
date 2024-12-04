from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import fitz  # PyMuPDF
from typing import List

# Define the default folder containing PDFs
PDF_FOLDER = "folder"  # Update this path to your PDF folder

app = FastAPI()

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Mount the directory containing the PDF files to serve them
app.mount("/files", StaticFiles(directory=PDF_FOLDER), name="files")


class SearchRequest(BaseModel):
    keyword: str


@app.post("/search")
def search_pdfs(request: SearchRequest):
    keyword = request.keyword
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword is required")

    results = []
    for root, _, files in os.walk(PDF_FOLDER):
        for file in files:
            if file.endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                if contains_keyword(pdf_path, keyword):
                    results.append(f"/files/{file}")  # Return relative path for frontend links

    return {"results": results}


@app.post("/highlight")
def highlight_pdf(request: SearchRequest):
    keyword = request.keyword
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword is required")

    annotated_files = []
    for root, _, files in os.walk(PDF_FOLDER):
        for file in files:
            if file.endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                if contains_keyword(pdf_path, keyword):
                    output_path = add_highlight_to_pdf(pdf_path, keyword)
                    annotated_files.append(f"/files/{os.path.basename(output_path)}")

    return {"annotated_files": annotated_files}


def contains_keyword(pdf_path: str, keyword: str) -> bool:
    try:
        with fitz.open(pdf_path) as pdf:
            for page in pdf:
                if keyword.lower() in page.get_text().lower():
                    return True
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return False


def add_highlight_to_pdf(pdf_path: str, keyword: str) -> str:
    output_path = pdf_path.replace(".pdf", "_highlighted.pdf")
    try:
        with fitz.open(pdf_path) as pdf:
            for page in pdf:
                text_instances = page.search_for(keyword)
                for inst in text_instances:
                    page.add_highlight_annot(inst)
            pdf.save(output_path, garbage=4, deflate=True)
        return output_path
    except Exception as e:
        print(f"Error highlighting PDF: {e}")
        return pdf_path
