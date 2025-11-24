import os
import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from app.converter import PDFToEpubConverter
from app.jobs import job_manager

app = FastAPI(title="PDF to ePub Converter")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

def remove_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

def process_pdf_task(job_id: str, pdf_bytes: bytes):
    try:
        def progress_callback(p):
            job_manager.update_progress(job_id, p)

        converter = PDFToEpubConverter(pdf_bytes, progress_callback=progress_callback)
        epub_path = converter.convert()
        job_manager.set_complete(job_id, epub_path)
    except Exception as e:
        job_manager.set_error(job_id, str(e))

@app.post("/api/upload", summary="Start PDF conversion job")
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if file.content_type != "application/pdf" and not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail=f"Invalid file type: {file.content_type}. Only PDF allowed.")

    content = await file.read()
    job_id = job_manager.create_job(filename=file.filename)

    # Run in background
    background_tasks.add_task(process_pdf_task, job_id, content)

    return {"job_id": job_id}

@app.get("/api/status/{job_id}", summary="Check job status")
def get_status(job_id: str):
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/api/download/{job_id}", summary="Download result")
def download_result(job_id: str, background_tasks: BackgroundTasks):
    job = job_manager.get_job(job_id)
    if not job or job["status"] != "completed":
        raise HTTPException(status_code=404, detail="Result not ready or job not found")

    path = job["result_path"]
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File expired or removed")

    # Clean up after download?
    # For a simple web app, maybe we keep it for a bit.
    # Or we can schedule removal after this download.
    # Let's schedule removal to keep disk clean, assuming single download.
    # background_tasks.add_task(remove_file, path)

    # Determine filename
    original_name = job.get("filename", "converted.pdf")
    base_name = os.path.splitext(original_name)[0]
    download_name = f"{base_name}.epub"

    return FileResponse(
        path=path,
        filename=download_name,
        media_type="application/epub+zip"
    )

@app.get("/")
def read_root():
    return FileResponse("app/static/index.html")

# Keep the old endpoint for backward compatibility if needed,
# or remove it. I'll remove it to keep code clean as per plan implies replacement.
