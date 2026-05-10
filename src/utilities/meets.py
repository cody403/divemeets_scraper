"""This module hosts the meets class which is an abstration of the
information about meets"""
from lib.scraper_helpers import get_html_tree_from_url


class MeetResults():
    BASE_RESULTS_URL = "https://new.divemeets.com/MeetResults/"

    def __init__(self, meet_number : str):
        self.url = f"{self.BASE_RESULTS_URL}{meet_number}"
        self.page_tree = get_html_tree_from_url(self.url)


    def get_event_links(self):
        print(self.page_tree)
        

if "__main__" in __name__:
    MeetResults("12852")