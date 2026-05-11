""""""
from typing import Dict, Optional

from lxml import html
from playwright.sync_api import sync_playwright


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/121.0.0.0 Safari/537.36"
)


def get_html_tree_from_url(
    url: str,
    referer: Optional[str] = None,
    extra_headers: Optional[Dict[str, str]] = None,
):
    headers: Dict[str, str] = {
        "accept-language": "en-US,en;q=0.9",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "user-agent": DEFAULT_USER_AGENT,
    }
    if referer:
        headers["referer"] = referer
    if extra_headers:
        headers.update(extra_headers)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(locale="en-US")
        page = context.new_page()
        page.set_extra_http_headers(headers)
        page.goto(url, wait_until="networkidle")
        content = page.content()
        browser.close()

    tree = html.fromstring(content)
    return tree