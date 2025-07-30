#!/usr/bin/env python3
"""
novel_downloader.core.exporters.epub_utils.text_to_html
-------------------------------------------------------

Module for converting raw chapter text to formatted HTML,
with automatic word correction and optional image/tag support.
"""

import json
import logging
import re
from pathlib import Path
from typing import Any

from novel_downloader.utils.constants import (
    EPUB_IMAGE_WRAPPER,
    REPLACE_WORD_MAP_PATH,
)
from novel_downloader.utils.network import download_image
from novel_downloader.utils.text_utils import diff_inline_display

logger = logging.getLogger(__name__)

_IMG_TAG_PATTERN = re.compile(
    r'<img\s+[^>]*src=[\'"]([^\'"]+)[\'"][^>]*>', re.IGNORECASE
)


# Load and sort replacement map from JSON
try:
    replace_map_raw = REPLACE_WORD_MAP_PATH.read_text(encoding="utf-8")
    REPLACE_WORDS_MAP = json.loads(replace_map_raw)
    REPLACE_WORDS_MAP = dict(
        sorted(REPLACE_WORDS_MAP.items(), key=lambda x: len(x[0]), reverse=True)
    )
except Exception as e:
    REPLACE_WORDS_MAP = {}
    logger.info(
        f"[epub] Failed to load REPLACE_WORDS_MAP from {REPLACE_WORD_MAP_PATH}: {e}"
    )


def _check_and_correct_words(txt_str: str) -> str:
    """
    Perform word replacement using REPLACE_WORDS_MAP.

    :param txt_str: Raw string of text.
    :return: String with corrected words.
    """
    for k, v in REPLACE_WORDS_MAP.items():
        txt_str = txt_str.replace(k, v)
    return txt_str


def chapter_txt_to_html(
    chapter_title: str,
    chapter_text: str,
    author_say: str,
) -> str:
    """
    Convert chapter text and author note to styled HTML.

    :param chapter_title: Title of the chapter.
    :param chapter_text: Main content of the chapter.
    :param author_say: Optional author note content.
    :return: Rendered HTML as a string.
    """

    def _render_lines(text: str) -> str:
        parts = []
        for line in text.strip().splitlines():
            line = line.strip()
            if not line:
                continue

            if (
                line.startswith("<img")
                and line.endswith("/>")
                or line.startswith('<div class="duokan-image-single illus">')
                and line.endswith("</div>")
            ):
                parts.append(line)
            else:
                corrected = _check_and_correct_words(line)
                if corrected != line:
                    diff = diff_inline_display(line, corrected)
                    logger.info("[epub] Correction diff:\n%s", diff)
                parts.append(f"<p>{corrected}</p>")
        return "\n".join(parts)

    html_parts = [f"<h2>{chapter_title}</h2>"]
    html_parts.append(_render_lines(chapter_text))

    if author_say.strip():
        html_parts.extend(["<hr />", "<p>作者说:</p>", _render_lines(author_say)])

    return "\n".join(html_parts)


def inline_remote_images(
    content: str,
    image_dir: str | Path,
) -> str:
    """
    Download every remote `<img src="...">` in `content` into `image_dir`,
    and replace the original tag with EPUB_IMAGE_WRAPPER
    pointing to the local filename.

    :param content: HTML/text of the chapter containing <img> tags.
    :param image_dir: Directory to save downloaded images into.
    :return: Modified content with local image references.
    """

    def _replace(match: re.Match[str]) -> str:
        url = match.group(1)
        try:
            # download_image returns a Path or None
            local_path = download_image(
                url, image_dir, target_name=None, on_exist="skip"
            )
            if not local_path:
                logger.warning(
                    "Failed to download image, leaving original tag: %s", url
                )
                return match.group(0)

            # wrap with the EPUB_IMAGE_WRAPPER, inserting just the filename
            return EPUB_IMAGE_WRAPPER.format(filename=local_path.name)
        except Exception:
            logger.exception("Error processing image URL: %s", url)
            return match.group(0)

    return _IMG_TAG_PATTERN.sub(_replace, content)


def generate_book_intro_html(book_info: dict[str, Any]) -> str:
    """
    Generate HTML string for a book's information and summary.

    This function takes a dictionary containing book details and formats
    it into a styled HTML block, skipping any missing fields gracefully.

    :param book_info: A dictionary containing keys like 'book_name'...

    :return: An HTML-formatted string presenting the book's information.
    """
    book_name = book_info.get("book_name")
    author = book_info.get("author")
    serial_status = book_info.get("serial_status")
    word_count = book_info.get("word_count")
    summary = book_info.get("summary", "").strip()

    # Start composing the HTML output
    html_parts = ["<h1>书籍简介</h1>", '<div class="list">', "<ul>"]

    if book_name:
        html_parts.append(f"<li>书名: 《{book_name}》</li>")
    if author:
        html_parts.append(f"<li>作者: {author}</li>")

    if word_count:
        html_parts.append(f"<li>字数: {word_count}</li>")
    if serial_status:
        html_parts.append(f"<li>状态: {serial_status}</li>")

    html_parts.append("</ul>")
    html_parts.append("</div>")
    html_parts.append('<p class="new-page-after"><br/></p>')

    if summary:
        html_parts.append("<h2>简介</h2>")
        for paragraph in summary.split("\n"):
            paragraph = paragraph.strip()
            if paragraph:
                html_parts.append(f"<p>{paragraph}</p>")

    return "\n".join(html_parts)
