import fitz
import os

def create_dummy_pdf(filename="test.pdf"):
    doc = fitz.open()

    # Page 1: Title and Chapter 1
    page = doc.new_page()
    page.insert_text((50, 50), "My Test Book", fontsize=24)
    page.insert_text((50, 100), "Chapter 1", fontsize=18)
    page.insert_text((50, 150), "This is the first paragraph of the first chapter.", fontsize=12)
    page.insert_text((50, 170), "It continues here.", fontsize=12)

    # Test spacing issues
    # "Hello" and "World" without explicit space in strings, but positioned with space
    page.insert_text((50, 200), "Hello", fontsize=12)
    page.insert_text((80, 200), "World", fontsize=12)

    # Explicit space span
    page.insert_text((50, 220), "Good", fontsize=12)
    page.insert_text((80, 220), " ", fontsize=12)
    page.insert_text((85, 220), "Morning", fontsize=12)

    # Header artifact
    page.insert_text((200, 20), "My Test Book Header", fontsize=10)
    # Page number
    page.insert_text((300, 800), "1", fontsize=10)

    # Page 2: More content for Chapter 1
    page = doc.new_page()
    page.insert_text((200, 20), "My Test Book Header", fontsize=10)
    page.insert_text((50, 50), "This is the second page of the first chapter.", fontsize=12)
    page.insert_text((300, 800), "2", fontsize=10)

    # Page 3: Chapter 2
    page = doc.new_page()
    page.insert_text((200, 20), "My Test Book Header", fontsize=10)
    page.insert_text((50, 100), "Chapter 2", fontsize=18)
    page.insert_text((50, 150), "This is the second chapter.", fontsize=12)
    page.insert_text((300, 800), "3", fontsize=10)

    doc.save(filename)
    print(f"Created {filename}")

if __name__ == "__main__":
    # Create in the same directory
    path = os.path.join(os.path.dirname(__file__), 'test.pdf')
    create_dummy_pdf(path)
