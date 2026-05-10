""""""
import requests
from lxml import html


def get_html_tree_from_url(url : str) -> str:
    page = requests.get(url)
    tree = html.fromstring(page)
    return tree