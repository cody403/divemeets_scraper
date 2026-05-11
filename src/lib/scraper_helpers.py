""""""
from lxml import html
from playwright.sync_api import sync_playwright


def get_html_tree_from_url(url : str):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        content = page.content()
        browser.close()
    
    tree = html.fromstring(content)
    return tree