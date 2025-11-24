import io
import fitz  # pymupdf
from ebooklib import epub
import re
from collections import Counter
import tempfile
import os
import html

class PDFToEpubConverter:
    def __init__(self, pdf_bytes, progress_callback=None):
        self.doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        self.book = epub.EpubBook()
        self.pages_content = []  # List of list of text blocks
        self.progress_callback = progress_callback

    def extract_text(self):
        """
        Extracts text blocks from the PDF.
        Aggregates spans into lines and paragraphs to preserve sentence structure.
        """
        total_pages = len(self.doc)
        for i, page in enumerate(self.doc):
            if self.progress_callback:
                # Phase 1: Extraction is roughly 50% of the work
                self.progress_callback(int((i / total_pages) * 50))

            blocks = page.get_text("dict")["blocks"]
            page_blocks = []
            for b in blocks:
                if b['type'] == 0:  # text block
                    # Aggregate lines in this block
                    block_text_parts = []
                    block_size_accum = 0
                    block_char_count = 0

                    # We'll use the bounding box of the first line/span for position checking
                    block_bbox = b["bbox"]

                    for l in b["lines"]:
                        line_text_parts = []
                        for s in l["spans"]:
                            text = s["text"]
                            if text:
                                line_text_parts.append(text)
                                block_size_accum += s["size"] * len(text)
                                block_char_count += len(text)

                        if line_text_parts:
                             # Join spans in a line. Spans are usually adjacent.
                             # Sometimes we might need space if they are far apart, but usually straightforward.
                             line_str = "".join(line_text_parts)
                             block_text_parts.append(line_str)

                    if block_text_parts:
                        full_text = " ".join(block_text_parts).strip() # Join lines with space

                        # Calculate weighted average font size for the block
                        avg_size = block_size_accum / block_char_count if block_char_count > 0 else 12

                        if full_text:
                            page_blocks.append({
                                "text": full_text,
                                "size": avg_size,
                                "bbox": block_bbox,
                            })
            self.pages_content.append(page_blocks)

    def detect_and_remove_artifacts(self):
        """Detects and removes headers, footers, and page numbers."""
        if not self.pages_content:
            return

        top_candidates = Counter()
        bottom_candidates = Counter()

        # Get page height from the first page
        try:
            height = self.doc[0].rect.height
        except Exception:
            height = 842  # Default A4 height fallback

        header_threshold = height * 0.1
        footer_threshold = height * 0.9

        def normalize_artifact_text(t):
            # Remove digits and whitespace to catch "2 HEADER" vs "4 HEADER"
            return re.sub(r'[\d\s]+', '', t).lower()

        # 1. Identify potential repeating artifacts
        for page_blocks in self.pages_content:
            for block in page_blocks:
                y0 = block['bbox'][1]
                text = block['text']
                norm_text = normalize_artifact_text(text)

                if not norm_text: # Skip empty after normalization
                    continue

                if y0 < header_threshold:
                    top_candidates[norm_text] += 1
                elif y0 > footer_threshold:
                    bottom_candidates[norm_text] += 1

        # Threshold: if text appears on more than 30% of pages (min 2 pages)
        threshold_count = max(2, len(self.pages_content) * 0.3)

        # Debug print
        with open("debug_artifacts.txt", "w") as f:
            f.write(f"Top candidates: {top_candidates.most_common(20)}\n")
            f.write(f"Bottom candidates: {bottom_candidates.most_common(20)}\n")
            f.write(f"Threshold: {threshold_count}\n")

        artifacts = set()
        for text, count in top_candidates.items():
            if count > threshold_count:
                artifacts.add(text)
        for text, count in bottom_candidates.items():
            if count > threshold_count:
                artifacts.add(text)

        # 2. Filter content
        # Strict zone: Remove anything very close to edges regardless of frequency
        # Headers are at ~34, Body at ~70. Safe cut: 50.
        strict_top_limit = 50 
        strict_bottom_limit = height - 50

        cleaned_pages = []
        for page_blocks in self.pages_content:
            cleaned_page = []
            for block in page_blocks:
                text = block['text']
                y0 = block['bbox'][1]

                # 1. Strict Zone Check
                if y0 < strict_top_limit or y0 > strict_bottom_limit:
                    continue

                # 2. Page Number Check (for things slightly outside strict zone)
                is_page_number = re.match(r'^\d+$', text) and (y0 < header_threshold or y0 > footer_threshold)

                # 3. Known Artifacts Check
                is_known_artifact = False
                artifact_patterns = [
                    r"This content downloaded from",
                    r"All use subject to https://about.jstor.org",
                    r"about.jstor.org/terms"
                ]
                for pattern in artifact_patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        is_known_artifact = True
                        break
                
                # 4. Repeating Artifact Check
                norm_text = normalize_artifact_text(text)
                is_repeating_artifact = norm_text in artifacts

                if not is_repeating_artifact and not is_page_number and not is_known_artifact:
                    cleaned_page.append(block)
            cleaned_pages.append(cleaned_page)

        self.pages_content = cleaned_pages

    def detect_chapters(self):
        """
        Detects chapters based on heuristics:
        1. Starts with 'Chapter', 'Part', 'Book'
        2. Significant font size difference
        """
        if not self.pages_content:
            return []

        # Collect all font sizes to find average/median
        all_sizes = [block['size'] for page in self.pages_content for block in page]
        if not all_sizes:
            return []

        avg_size = sum(all_sizes) / len(all_sizes)

        chapters = []
        # Initialize with a default chapter in case no chapters are detected immediately
        current_chapter = {"title": "Introduction", "content": []}

        chapter_keywords = re.compile(r'^(chapter|part|book)\s+\d+', re.IGNORECASE)

        for page_blocks in self.pages_content:
            for block in page_blocks:
                text = block['text']
                size = block['size']

                is_new_chapter = False

                # Heuristic 1: Keyword
                if chapter_keywords.match(text):
                    is_new_chapter = True

                # Heuristic 2: Large font (e.g., > 1.5x average)
                # We also check that the text length is short to avoid bolded paragraphs
                elif size > avg_size * 1.5 and len(text) < 80:
                    # Only treat as chapter if it doesn't end with punctuation usually found in sentences
                    if not text.strip().endswith('.'):
                         is_new_chapter = True

                if is_new_chapter:
                    # Save previous chapter if it has content
                    if current_chapter["content"]:
                        chapters.append(current_chapter)
                    current_chapter = {"title": text, "content": []}
                else:
                    # Check if we should merge with the previous paragraph
                    # If previous paragraph doesn't end with sentence punctuation, likely a split sentence
                    if current_chapter["content"]:
                        prev_para = current_chapter["content"][-1].strip()
                        # Check for sentence-ending punctuation (., ?, !, or closing quotes/parens)
                        if not re.search(r'[.?!”’"\'\)\]]$', prev_para):
                             current_chapter["content"][-1] = current_chapter["content"][-1] + " " + text
                        else:
                             current_chapter["content"].append(text)
                    else:
                        current_chapter["content"].append(text)

        # Append the last chapter
        if current_chapter["content"] or current_chapter["title"] != "Introduction":
            chapters.append(current_chapter)

        # If we only have "Introduction" with content and no other detected chapters, just return it
        if len(chapters) == 0 and current_chapter["content"]:
             chapters.append(current_chapter)

        return chapters

    def convert(self) -> str:
        """
        Orchestrates the conversion and returns the path to the generated epub.
        """
        self.extract_text()

        if self.progress_callback:
            self.progress_callback(60)

        self.detect_and_remove_artifacts()

        if self.progress_callback:
            self.progress_callback(70)

        chapters_data = self.detect_chapters()

        if self.progress_callback:
            self.progress_callback(80)

        # Setup Epub
        self.book.set_identifier('id123456')
        self.book.set_title('Converted Book')
        self.book.set_language('en')
        self.book.add_author('Unknown') # Could extract from PDF metadata if available

        epub_chapters = []
        for i, chap_data in enumerate(chapters_data):
            file_name = f'chap_{i}.xhtml'
            c = epub.EpubHtml(title=chap_data['title'], file_name=file_name, lang='en')

            # Build HTML content
            title_html = f"<h1>{html.escape(chap_data['title'])}</h1>"

            # Simple paragraph construction
            body_html = ""
            for para in chap_data['content']:
                body_html += f"<p>{html.escape(para)}</p>"

            c.content = title_html + body_html
            self.book.add_item(c)
            epub_chapters.append(c)

        # Table of Contents
        self.book.toc = (epub_chapters)

        # Add NCX and Nav
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

        # CSS
        style = 'body { font-family: Helvetica, Arial, sans-serif; } h1 { text-align: center; } p { text-align: justify; }'
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
        self.book.add_item(nav_css)

        self.book.spine = ['nav'] + epub_chapters

        # Create a temporary file for the output
        # We rely on the caller to clean this up or we return bytes
        fd, path = tempfile.mkstemp(suffix=".epub")
        os.close(fd)

        epub.write_epub(path, self.book)

        if self.progress_callback:
            self.progress_callback(100)

        return path
