"""This module hosts the meets class which is an abstration of the
information about meets"""
import re
from lib.scraper_helpers import get_html_tree_from_url


class MeetResults():
    BASE_RESULTS_URL = "https://new.divemeets.com/MeetResults/"
    EVENT_LINK_RE = re.compile(
        r'^(?:https?://new\.divemeets\.com)?/EventResults/(?P<meet>\d+)/(?P<event>\d+)/(?P<type>\d+)',
        re.IGNORECASE,
    )

    def __init__(self, meet_number: str):
        self.meet_number = str(meet_number)
        self.url = f"{self.BASE_RESULTS_URL}{self.meet_number}"
        self.page_tree = get_html_tree_from_url(self.url)

    def get_meet_name(self):
        texts = [
            t.strip() for t in self.page_tree.xpath('//div[contains(@class, "container-top")]//text()')
            if t.strip()
        ]
        filtered = [
            t for t in texts
            if t not in {
                "Meet Results",
                "Event Results",
                "Board Assignments",
                "Official Scores",
                "Events",
                "Entries",
                "Date",
            }
        ]
        if filtered:
            return filtered[0]
        return f"Meet {self.meet_number}"

    def get_associated_events(self):
        events = []
        seen = set()
        anchors = self.page_tree.xpath('//a[contains(@href, "EventResults/")]')

        for anchor in anchors:
            href = (anchor.get('href') or '').strip()
            if not href:
                continue

            match = self.EVENT_LINK_RE.search(href)
            if not match:
                continue

            meet = match.group('meet')
            if meet != self.meet_number:
                continue

            event_number = match.group('event')
            event_type = match.group('type')
            key = (event_number, event_type)
            if key in seen:
                continue

            seen.add(key)
            full_url = href if href.startswith('http') else f'https://new.divemeets.com{href}'
            label = anchor.text_content().strip()

            events.append({
                'meet_number': meet,
                'event_number': event_number,
                'event_type': event_type,
                'url': full_url,
                'label': label,
            })

        return events
        
