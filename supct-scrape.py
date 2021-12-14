import datetime
import argparse

from download import get_urls, download_judgms

def scrape(year="All", meta_only=True):
  # Filter bad arguments 
  if year != "All" and (not year.isnumeric() or int(year) < 2000 
  or int(year) > datetime.datetime.now().year):
    print("Invalid date")
    return

  # Get metadata
  get_urls(year)

  # Get judgment text (HTML)
  if not meta_only:
    download_judgms()

if __name__ == "__main__":
  # Simple CLI interface 
  parser = argparse.ArgumentParser(description="Scrape judiciary website cases")
  parser.add_argument("year", 
    metavar="year", 
    type=str, 
    help="Year to scrape (use 'All' to scrape all cases to date)")
  parser.add_argument("--meta-only", "-m",
    action="store_true", 
    default="False",
    help="Scrape only case metadata, omitting main text")
  args = parser.parse_args()

  scrape(year=args.year, meta_only=args.meta_only)