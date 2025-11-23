import sys
import os
sys.path.append(os.getcwd())
from app.converter import PDFToEpubConverter
import shutil

pdf_path = r"c:\Users\mckru\Documents\pdf-epub\pdf-to-epub\verification\Society and Economy - Granovetter.pdf"
output_path = r"c:\Users\mckru\Documents\pdf-epub\pdf-to-epub\verification\converted_fixed.epub"

def run_conversion():
    print(f"Converting {pdf_path}...")
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    converter = PDFToEpubConverter(pdf_bytes)
    temp_path = converter.convert()
    
    shutil.move(temp_path, output_path)
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    run_conversion()
