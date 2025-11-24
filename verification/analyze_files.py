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
        
        # Check pages up to 100
        for i in range(100):
            page = doc[i]
            if i == 98: # Page 99 (Book Page 88)
                print(f"--- Page {i+1} (Book Page 88?) ---")
                blocks = page.get_text("dict")["blocks"]
                for b in blocks:
                    if b['type'] == 0:
                         full_block_text = ""
                         for l in b["lines"]:
                             for s in l["spans"]:
                                 full_block_text += s["text"] + " "
                         print(f"BLOCK: {full_block_text[:100]}...")
                         print(f"       ...{full_block_text[-100:]}")
            
            if i == 99: # Page 100
                print(f"--- Page {i+1} ---")
                blocks = page.get_text("dict")["blocks"]
                if blocks:
                    b = blocks[0]
                    if b['type'] == 0:
                         print(f"START BLOCK: {b['lines'][0]['spans'][0]['text'][:100]}")

    except Exception as e:
        print(f"Error reading PDF: {e}")

def analyze_epub(path):
    print(f"\n--- Analyzing EPUB: {os.path.basename(path)} ---")
    try:
        book = epub.read_epub(path)
        
        items = list(book.get_items())
        html_items = [i for i in items if i.get_type() == ebooklib.ITEM_DOCUMENT]

        print("Scanning EPUB for 'Chung found'...")
        for item in html_items:
            content = item.get_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text()
            
            if "As I described" in text:
                idx = text.find("As I described")
                snippet = text[max(0, idx-200):idx+200]
                snippet = snippet.encode('ascii', 'ignore').decode('ascii')
                print(f"  Found 'As I described' in {item.file_name}: ...{snippet}...")

    except Exception as e:
        print(f"Error reading EPUB: {e}")

if __name__ == "__main__":
    analyze_pdf(pdf_path)
    analyze_epub(epub_path)
