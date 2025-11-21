import os
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from app.converter import PDFToEpubConverter

app = FastAPI(title="PDF to ePub Converter")

def remove_file(path: str):
    try:
        os.remove(path)
    except Exception:
        pass

@app.post("/convert", summary="Convert PDF to ePub")
async def convert_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # Relaxed content type check, because it relies on client sending correct type
    if file.content_type != "application/pdf" and not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail=f"Invalid file type: {file.content_type}. Only PDF allowed.")

    try:
        content = await file.read()
        converter = PDFToEpubConverter(content)
        epub_path = converter.convert()

        # Determine filename
        original_name = file.filename or "book.pdf"
        base_name = os.path.splitext(original_name)[0]
        epub_filename = f"{base_name}.epub"

        # Schedule file removal
        background_tasks.add_task(remove_file, epub_path)

        return FileResponse(
            path=epub_path,
            filename=epub_filename,
            media_type="application/epub+zip"
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": f"Conversion failed: {str(e)}"})

@app.get("/")
def read_root():
    return {"message": "Welcome to PDF to ePub Converter. Use POST /convert to convert files."}
