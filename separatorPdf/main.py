import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PyPDF2 import PdfReader, PdfWriter
from typing import List
from io import BytesIO
import base64

app = FastAPI()

@app.post("/dividir")
async def dividir_pdf(file: UploadFile = File(...)):
    """
    Recibe un archivo PDF, lo divide cada 2 páginas y devuelve los PDFs como base64.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")

    try:
        # Leer archivo en memoria
        contenido_pdf = await file.read()
        lector = PdfReader(BytesIO(contenido_pdf))
        total_paginas = len(lector.pages)
        archivos_generados: List[dict] = []

        for i in range(0, total_paginas, 2):
            escritor = PdfWriter()
            escritor.add_page(lector.pages[i])
            if i + 1 < total_paginas:
                escritor.add_page(lector.pages[i + 1])

            salida_buffer = BytesIO()
            escritor.write(salida_buffer)
            salida_buffer.seek(0)

            # Codificar el archivo PDF dividido a base64
            encoded_pdf = base64.b64encode(salida_buffer.read()).decode('utf-8')
            nombre = f"{file.filename[:-4]}_{i+1}_{min(i+2, total_paginas)}.pdf"

            archivos_generados.append({
                "nombre": nombre,
                "contenido_base64": encoded_pdf
            })

        return JSONResponse(content={
            "mensaje": "PDF dividido exitosamente",
            "archivos_generados": archivos_generados
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el PDF: {str(e)}")
