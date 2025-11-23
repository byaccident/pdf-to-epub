import fitz  # pymupdf
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import os

pdf_path = r"c:\Users\mckru\Documents\pdf-epub\pdf-to-epub\verification\Society and Economy - Granovetter.pdf"
epub_path = r"c:\Users\mckru\Documents\pdf-epub\pdf-to-epub\verification\converted_fixed.epub"

def analyze_pdf(path):
    print(f"--- Analyzing PDF: {os.path.basename(path)} ---")
    try:
        doc = fitz.open(path)
        print(f"Pages: {len(doc)}")
        print(f"Metadata: {doc.metadata}")
        
        # Check pages 10-30
        for i in range(10, min(30, len(doc))):
            page = doc[i]
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                if b['type'] == 0: # text
                    y0 = b['bbox'][1]
                    if y0 < 100: # Only look at top of page
                        print(f"  Page {i+1} Top Content: '{b['lines'][0]['spans'][0]['text'][:30]}...' Y0: {y0:.2f}")
            
            # print(f"Sample text: {preview}...")
            
    except Exception as e:
        print(f"Error reading PDF: {e}")

def analyze_epub(path):
    print(f"\n--- Analyzing EPUB: {os.path.basename(path)} ---")
    try:
        book = epub.read_epub(path)
        print(f"Title: {book.get_metadata('DC', 'title')}")
        
        items = list(book.get_items())
        print(f"Total items: {len(items)}")
        
        html_items = [i for i in items if i.get_type() == ebooklib.ITEM_DOCUMENT]
        print(f"HTML Documents: {len(html_items)}")
        
        # Check all HTML items for the artifact
        print("Scanning EPUB for artifacts...")
        found_artifact = False
        for item in html_items:
            content = item.get_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text()
            if "Problems of Explanation" in text:
                snippet = text[text.find('Problems of Explanation')-20:text.find('Problems of Explanation')+50]
                snippet = snippet.encode('ascii', 'ignore').decode('ascii')
                print(f"  Found artifact in {item.file_name}: ...{snippet}...")
                found_artifact = True
        
        if not found_artifact:
            print("  No 'Problems of Explanation' artifacts found in EPUB.")

        if not found_artifact:
            print("  No 'Problems of Explanation' artifacts found in EPUB (except potentially in TOC).")

        print("\n--- Chapter Previews ---")
        for i, item in enumerate(html_items):
            content = item.get_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            preview = soup.get_text()[:200].replace('\n', ' ')
            preview = preview.encode('ascii', 'ignore').decode('ascii')
            print(f"Chapter {i} ({item.file_name}): {preview}...")
            
    except Exception as e:
        print(f"Error reading EPUB: {e}")

if __name__ == "__main__":
    analyze_pdf(pdf_path)
    analyze_epub(epub_path)
