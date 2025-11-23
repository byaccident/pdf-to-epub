# PDF to ePub Converter

A FastAPI application to convert PDF books into ePub format. This tool is designed to improve the reading experience on e-readers by:
- Extracting text from PDFs.
- Automatically detecting and removing headers, footers, and page numbers.
- Detecting chapters and generating a Table of Contents (TOC).
- Preserving paragraph structure.

## Prerequisites

- Python 3.12+
- `uv` (Project and package manager)

## Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   uv sync
   ```

## Usage

### Starting the Server

Run the FastAPI server using `uv`:

```bash
uv run uvicorn app.main:app --reload
```

The server will start at `http://127.0.0.1:8000`.

### Web Interface

Open your browser and navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000).
You will see a user-friendly interface where you can upload a PDF file, view the real-time conversion progress, and download the resulting ePub file.

### API Documentation

FastAPI provides automatic interactive documentation. Once the server is running, visit:
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### API Usage

You can also use the API programmatically. The application exposes an asynchronous job-based API:

1. **Upload PDF**: `POST /api/upload`
   - Returns a `job_id`.
2. **Check Status**: `GET /api/status/{job_id}`
   - Returns status (`queued`, `processing`, `completed`, `failed`) and progress percentage.
3. **Download Result**: `GET /api/download/{job_id}`
   - Downloads the generated ePub when status is `completed`.

**Example using Python:**

```python
import requests
import time

base_url = "http://127.0.0.1:8000"
files = {'file': ('book.pdf', open('book.pdf', 'rb'), 'application/pdf')}

# 1. Start Job
response = requests.post(f"{base_url}/api/upload", files=files)
job_id = response.json()['job_id']
print(f"Job started: {job_id}")

# 2. Poll Status
while True:
    status_res = requests.get(f"{base_url}/api/status/{job_id}").json()
    print(f"Status: {status_res['status']} ({status_res['progress']}%)")

    if status_res['status'] == 'completed':
        break
    if status_res['status'] == 'failed':
        print("Error:", status_res.get('error'))
        exit(1)
    time.sleep(1)

# 3. Download
download_res = requests.get(f"{base_url}/api/download/{job_id}")
with open('book.epub', 'wb') as f:
    f.write(download_res.content)
print("Download complete.")
```

## Development

To run the included tests:

```bash
# Create a dummy PDF for testing
uv run python tests/create_pdf.py

# Run the API test
uv run python tests/test_api.py
```
