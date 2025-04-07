import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PyPDF2 import PdfReader, PdfWriter
from typing import List
import shutil

app = FastAPI()

# Directorios donde se guardan archivos temporales
UPLOAD_FOLDER = "/home/tu_usuario/pdfuploads"
OUTPUT_FOLDER = "/home/tu_usuario/pdftemp"

# Crear carpetas si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.post("/dividir")
async def dividir_pdf(file: UploadFile = File(...)):
    """
    Recibe un archivo PDF, lo divide cada 2 páginas y devuelve los nombres de salida.
    """
    # Validación del archivo
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")

    # Guardar archivo en disco temporalmente
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        lector = PdfReader(filepath)
        total_paginas = len(lector.pages)
        nombres_salidas: List[str] = []

        for i in range(0, total_paginas, 2):
            escritor = PdfWriter()
            escritor.add_page(lector.pages[i])
            if i + 1 < total_paginas:
                escritor.add_page(lector.pages[i + 1])

            nombre_salida = f"{file.filename[:-4]}_{i+1}_{min(i+2, total_paginas)}.pdf"
            ruta_salida = os.path.join(OUTPUT_FOLDER, nombre_salida)

            with open(ruta_salida, "wb") as salida_pdf:
                escritor.write(salida_pdf)

            nombres_salidas.append(nombre_salida)

        return JSONResponse(content={
            "mensaje": "PDF dividido exitosamente",
            "archivos_generados": nombres_salidas
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el PDF: {str(e)}")
