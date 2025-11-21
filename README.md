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

### API Documentation

FastAPI provides automatic interactive documentation. Once the server is running, visit:
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Converting a PDF

You can use the `/convert` endpoint to convert a PDF file.

**Example using `curl`:**

```bash
curl -X POST "http://127.0.0.1:8000/convert" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/book.pdf;type=application/pdf" \
  --output converted_book.epub
```

**Example using Python (requests):**

```python
import requests

url = "http://127.0.0.1:8000/convert"
# Note: Ensure the file is opened in binary mode
# and optionally specify the mime type if needed
files = {'file': ('book.pdf', open('book.pdf', 'rb'), 'application/pdf')}
response = requests.post(url, files=files)

if response.status_code == 200:
    with open('book.epub', 'wb') as f:
        f.write(response.content)
else:
    print("Error:", response.text)
```

## Development

To run the included tests:

```bash
# Create a dummy PDF for testing
uv run python tests/create_pdf.py

# Run the API test
uv run python tests/test_api.py
```
