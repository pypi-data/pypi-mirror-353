"""
Network helpers: download Project Euler problems or RSS feeds.
"""
from __future__ import annotations
from bs4 import BeautifulSoup

import html
import os
import re
import textwrap
from datetime import date
from pathlib import Path
from typing import Final

import requests

BASE_URL: Final = "https://projecteuler.net"
MINIMAL_URL_TMPL: Final = BASE_URL + "/minimal={:d}"
RSS_URL: Final = BASE_URL + "/rss2_euler.xml"


class NetworkError(RuntimeError):
    pass

def get_problem_html(n: int, as_markdown: bool = True) -> str:
    """Download and optionally convert Project Euler problem to Markdown."""
    url = MINIMAL_URL_TMPL.format(n)
    resp = requests.get(url, timeout=30)
    if resp.status_code != 200:
        raise NetworkError(f"Project Euler returned HTTP {resp.status_code} for {url!r}")

    html_raw = resp.text.strip()
    if not as_markdown:
        return html_raw

    # Convert to Markdown-ish
    soup = BeautifulSoup(html_raw, "html.parser")

    md_lines = []
    for el in soup.find_all(["p", "br"], recursive=True):
        if el.name == "p":
            text = el.get_text().strip()
            md_lines.append(f"\n{text}\n")
        elif el.name == "br":
            md_lines.append("\n")

    content = "".join(md_lines).strip()

    return content



def scrape_title(snippet: str) -> str:
    """
    Extract the problem title from the minimal HTML snippet.

    The snippet always starts with <p>Problem NNN: *title*</p>
    """
    m = re.match(r"\s*<p>(?:Problem|Problem&nbsp;)\d+:\s*(.+?)</p>", snippet)
    return html.unescape(m.group(1)) if m else f"Problem"


def fetch_rss() -> str:
    """Return the raw Project Euler RSS feed."""
    resp = requests.get(RSS_URL, timeout=30)
    if resp.status_code != 200:
        raise NetworkError(f"Project Euler RSS fetch failed (HTTP {resp.status_code})")
    return resp.text
