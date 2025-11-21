from playwright.sync_api import sync_playwright, expect
import os
import time

def verify_frontend():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Go to the homepage
        page.goto("http://127.0.0.1:8000/")

        # 2. Check title and elements
        expect(page).to_have_title("PDF to ePub Converter")
        expect(page.locator("h1")).to_have_text("PDF to ePub Converter")
        expect(page.locator("#fileInput")).to_be_visible()
        expect(page.locator("#convertBtn")).to_be_visible()

        # 3. Take initial screenshot
        page.screenshot(path="verification/initial.png")

        # 4. Perform upload
        # We need a dummy PDF.
        if not os.path.exists("tests/test.pdf"):
            # Run create_pdf if needed, but tests/test.pdf should exist from previous steps
            import sys
            sys.path.append(".")
            from tests.create_pdf import create_dummy_pdf
            create_dummy_pdf("tests/test.pdf")

        page.locator("#fileInput").set_input_files("tests/test.pdf")
        page.locator("#convertBtn").click()

        # 5. Wait for progress or completion
        # It might go fast, so we might catch "Starting..." or "Processing"
        # Wait for result section to be visible
        try:
            expect(page.locator("#resultSection")).to_be_visible(timeout=10000)
        except:
            # Capture if it fails
            page.screenshot(path="verification/failed.png")
            raise

        # 6. Take success screenshot
        page.screenshot(path="verification/success.png")

        browser.close()

if __name__ == "__main__":
    verify_frontend()
