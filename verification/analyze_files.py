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
        
        # Check first 10 pages for Front Matter analysis
        for i in range(10):
            page = doc[i]
            print(f"\n--- Page {i+1} Content ---")
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                if b['type'] == 0:
                     full_block_text = ""
                     for l in b["lines"]:
                         for s in l["spans"]:
                             full_block_text += s["text"] + " "
                     safe_text = full_block_text.encode('ascii', 'ignore').decode('ascii')
                     print(f"BLOCK (y={b['bbox'][1]:.1f}): {safe_text[:100]}...")

    except Exception as e:
        print(f"Error reading PDF: {e}")

def analyze_epub(path):
    print(f"\n--- Analyzing EPUB: {os.path.basename(path)} ---")
    try:
        book = epub.read_epub(path)
        
        # List all items to debug cover
        print("EPUB Items:")
        for item in book.get_items():
            print(f"  ID: {item.get_id()} Type: {item.get_type()} Name: {item.file_name}")

        # Check for cover
        try:
            # ebooklib usually sets cover with id 'cover-img' or similar, let's check manifest
            cover_items = [i for i in book.get_items() if i.get_type() == ebooklib.ITEM_IMAGE]
            if cover_items:
                print(f"Cover Image Candidates: {len(cover_items)}")
                for ci in cover_items:
                    print(f"  Image: {ci.file_name} Size: {len(ci.content)}")
            else:
                print("No images found in EPUB.")
        except Exception as e:
            print(f"Error checking cover: {e}")
        
        items = list(book.get_items())
        html_items = [i for i in items if i.get_type() == ebooklib.ITEM_DOCUMENT]

        print("Scanning Front Matter (Chap 0) for structure...")
        if html_items:
            content = html_items[0].get_content().decode('utf-8')
            # print(f"Chap 0 Content Preview (first 500 chars):\n{content[:500]}")
            
            # Check for newlines in text (which indicate preserved structure)
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text()
            if "\n" in text:
                 print("  Confirmed: Newlines preserved in Front Matter.")
                 # Print a sample of preserved lines
                 lines = text.split('\n')
                 print("  Sample Lines:")
                 for l in lines[:5]:
                     print(f"    {l.strip()}")
            else:
                 print("  Warning: No newlines found in Front Matter text.")

    except Exception as e:
        print(f"Error reading EPUB: {e}")

if __name__ == "__main__":
    analyze_pdf(pdf_path)
    analyze_epub(epub_path)
