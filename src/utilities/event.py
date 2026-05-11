"""Event scraping helpers for DiveMeets."""
from urllib.parse import urljoin

from lib.scraper_helpers import get_html_tree_from_url


class EventResults:
    BASE_RESULTS_URL = "https://new.divemeets.com/EventResults/"
    REFERER_TEMPLATE = "https://new.divemeets.com/MeetResults/{meet_number}"

    def __init__(self, meet_number: str, event_number: str, event_type: str):
        self.meet_number = str(meet_number)
        self.event_number = str(event_number)
        self.event_type = str(event_type)
        self.url = f"{self.BASE_RESULTS_URL}{self.meet_number}/{self.event_number}/{self.event_type}"
        self.referer = self.REFERER_TEMPLATE.format(meet_number=self.meet_number)
        self.page_tree = get_html_tree_from_url(self.url, referer=self.referer)

    @staticmethod
    def _normalize_text(node):
        if node is None:
            return ""
        text = " ".join(node.xpath(".//text()"))
        text = text.replace("\xa0", " ")
        return " ".join(text.split())

    @staticmethod
    def _abs_url(href: str) -> str:
        if not href:
            return ""
        if href.startswith("http"):
            return href
        return urljoin("https://new.divemeets.com", href)

    def get_results(self):
        rows = self.page_tree.xpath('//div[contains(@class, "row rowback border")]')
        if not rows:
            rows = self.page_tree.xpath('//div[contains(@class, "rowback")]')

        results = []
        for row in rows:
            fullsize_cols = row.xpath('./div[contains(@class, "fullsize")]')
            if len(fullsize_cols) < 5:
                continue

            athlete_col = fullsize_cols[0]
            team_col = fullsize_cols[1]
            place_col = fullsize_cols[2]
            score_col = fullsize_cols[3]
            diff_col = fullsize_cols[4]

            athlete_profile_url = row.xpath('.//a[contains(@href, "Profile")]/@href')
            dive_sheet_url = row.xpath('.//a[contains(@href, "DiveSheetResults")]/@href')

            results.append({
                "meet_number": self.meet_number,
                "event_number": self.event_number,
                "event_type": self.event_type,
                "event_url": self.url,
                "athlete_name": self._normalize_text(athlete_col),
                "athlete_profile_url": self._abs_url(athlete_profile_url[0]) if athlete_profile_url else "",
                "team": self._normalize_text(team_col),
                "place": self._normalize_text(place_col),
                "score": self._normalize_text(score_col),
                "difference": self._normalize_text(diff_col),
                "dive_sheet_url": self._abs_url(dive_sheet_url[0]) if dive_sheet_url else "",
            })

        return results


def get_results(meet_number: str, event_number: str, event_type: str):
    return EventResults(meet_number, event_number, event_type).get_results()
