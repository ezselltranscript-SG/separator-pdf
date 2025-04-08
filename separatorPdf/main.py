from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
import zipfile

app = FastAPI()

@app.post("/dividir")
async def dividir_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")

    try:
        contenido_pdf = await file.read()
        lector = PdfReader(BytesIO(contenido_pdf))
        total_paginas = len(lector.pages)

        # Crear ZIP en memoria
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for i in range(0, total_paginas, 2):
                escritor = PdfWriter()
                escritor.add_page(lector.pages[i])
                if i + 1 < total_paginas:
                    escritor.add_page(lector.pages[i + 1])

                salida_buffer = BytesIO()
                escritor.write(salida_buffer)
                salida_buffer.seek(0)

                nombre_archivo = f"{file.filename[:-4]}_{i+1}_{min(i+2, total_paginas)}.pdf"
                zip_file.writestr(nombre_archivo, salida_buffer.read())

        zip_buffer.seek(0)
        return StreamingResponse(
            zip_buffer,
            media_type="application/x-zip-compressed",
            headers={"Content-Disposition": "attachment; filename=archivos_divididos.zip"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el PDF: {str(e)}")
