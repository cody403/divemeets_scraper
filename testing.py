import sys
from pathlib import Path
import re
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utilities.meet import MeetResults
from src.utilities.event import EventResults


def parse_meet_numbers(user_input: str) -> list:
    """Parse user input to extract meet numbers (separated by any non-digit character)."""
    numbers = re.findall(r'\d+', user_input)
    return numbers


def fetch_event_results(meet_number: str, event_number: str, event_type: str) -> list:
    """Fetch results for a single event."""
    try:
        event = EventResults(meet_number, event_number, event_type)
        return event.get_results()
    except Exception as e:
        print(f"Error fetching event {meet_number}/{event_number}/{event_type}: {e}")
        return []


def main():
    user_input = input("Which meets would you like to look at? ").strip()
    if not user_input:
        print("No meets provided. Exiting.")
        return

    meet_numbers = parse_meet_numbers(user_input)
    if not meet_numbers:
        print("No valid meet numbers found. Exiting.")
        return

    print(f"\nProcessing {len(meet_numbers)} meet(s): {', '.join(meet_numbers)}\n")

    for meet_number in meet_numbers:
        print(f"Fetching events for meet {meet_number}...")
        try:
            meet = MeetResults(meet_number)
            events = meet.get_associated_events()
            print(f"Found {len(events)} events for meet {meet_number}")

            if not events:
                print(f"No events found for meet {meet_number}")
                continue

            all_results = []

            # Asynchronously fetch results for all events
            print(f"Fetching results for all events in meet {meet_number}...")
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {
                    executor.submit(
                        fetch_event_results,
                        event['meet_number'],
                        event['event_number'],
                        event['event_type'],
                    ): event for event in events
                }

                completed = 0
                for future in as_completed(futures):
                    results = future.result()
                    all_results.extend(results)
                    completed += 1
                    print(f"  [{completed}/{len(events)}] Event completed")

            # Save to CSV
            if all_results:
                csv_filename = f"scraper_results/{meet_number}.csv"
                keys = all_results[0].keys()

                print(f"\nSaving {len(all_results)} result(s) to {csv_filename}...")
                with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(all_results)
                print(f"Saved to {csv_filename}")
            else:
                print(f"No results collected for meet {meet_number}")

        except Exception as e:
            print(f"Error processing meet {meet_number}: {e}")

    print("\nDone!")


if __name__ == "__main__":
    main()

