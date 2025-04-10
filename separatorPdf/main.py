import os
import shutil
import zipfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from PyPDF2 import PdfReader, PdfWriter
from typing import List

app = FastAPI()

# Directories
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output_pdfs"
ZIP_DIR = "zipped"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ZIP_DIR, exist_ok=True)

@app.post("/split")
async def split_pdf(file: UploadFile = File(...)):
    """
    Receives a PDF file, splits it every 2 pages, and returns a downloadable ZIP.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="The uploaded file must be a PDF.")

    # Save the original file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)
        output_files: List[str] = []

        # Get the filename without the .pdf extension
        base_name = file.filename[:-4]

        for i in range(0, total_pages, 2):
            writer = PdfWriter()
            writer.add_page(reader.pages[i])
            if i + 1 < total_pages:
                writer.add_page(reader.pages[i + 1])

            part_number = (i // 2) + 1
            output_filename = f"{base_name}_Part{part_number}.pdf"
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            with open(output_path, "wb") as out_pdf:
                writer.write(out_pdf)

            output_files.append(output_path)

        # Create ZIP file
        zip_filename = f"{base_name}_split.zip"
        zip_path = os.path.join(ZIP_DIR, zip_filename)
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for path in output_files:
                zipf.write(path, os.path.basename(path))

        # Return the ZIP as a download
        return FileResponse(path=zip_path, filename=zip_filename, media_type='application/zip')

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while processing PDF: {str(e)}")
