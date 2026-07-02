import asyncio
import sys
import webbrowser
import json
from yaml import load as yaml_load
from yaml import FullLoader
import utils

from requests.auth import HTTPBasicAuth

# Load configuration file
try:
  with open("config.yaml", "r") as f:
    content = f.read()
    CONFIG = yaml_load(content, Loader=FullLoader)
except FileNotFoundError:
  sys.exit(
    """
Mandatory configuration file "config.yaml" was not present.
"""
  )

# Global Constants
SAVED_SEARCHES = CONFIG["saved_searches"]
AUTH = HTTPBasicAuth(
  CONFIG["username"],
  CONFIG["api_key"]
)
FAVORITES_TAG = f"fav:{CONFIG['username']}"

# Site specific Constants
POST_URL_BASE = f"{CONFIG['web_base']}/posts/"
JSON_URL_BASE = f"{CONFIG['web_base']}/posts.json/"

class Browser:
  def __init__(self, browser_str: str, page_launch_type: str):
    self.browser_str: str = browser_str
    self.page_launch_type: str = page_launch_type
    self.browser = webbrowser
    self.browser.register(self.browser_str)

  def launch(self, url: str) -> None:
    if self.page_launch_type == "new_window":
      self.browser.open_new(url)
    else:
      self.browser.open_new_tab(url)

BROWSER = Browser(
  CONFIG["browser"],
  CONFIG["page_launch_type"]
)

async def get_most_recent_post_id(tag_str: str) -> int:
  "Returns the most recent post ID of the given tag string. If empty, returns 0"
  url = utils.construct_tagged_url(
    JSON_URL_BASE,
    tag_str
  )

  response = utils.fetch(
    url,
    auth=AUTH
  )

  # converts the response content into a list of dictionaries.
  try:
    image_set = json.loads(response.text)
  except json.decoder.JSONDecodeError as e:
    print(f"There was a problem loading the results from {url}")
    raise e

  # If results exist, return the first image id, else, return 0
  for image in image_set:
    return int(image.get("id"))
  else:
    return 0

async def compose_search_range(subset_tag: str, range_type) -> str:
  "Based on the range type, returns the search range of the subset tag."

  if range_type == "none":
    return ""
  elif range_type == "after":
    fetch_id_task = asyncio.create_task(
      get_most_recent_post_id(
        subset_tag
      )
    )

    id = await fetch_id_task
    return f"id:>{id}"
  elif range_type == "before":
    fetch_id_task = asyncio.create_task(
      get_most_recent_post_id(
        f"{subset_tag} order:id" 
      )
    )

    id = await fetch_id_task
    return f"id:<{id}"
  elif range_type == "between":
    max_id_task = asyncio.create_task(
      get_most_recent_post_id(
        subset_tag
      )
    )

    min_id_task = asyncio.create_task(
      get_most_recent_post_id(
        f"{subset_tag} order:id" 
      )
    )
    
    max_ = await max_id_task
    min_ = await min_id_task

    return f"id:{min_}..{max_}"
  else:
    raise ValueError(
      f"Provided range_type: {range_type} is not defined"
    )

async def process(saved_search: dict) -> None:
  "Takes in a saved search, prepares it, and launches it in a web browser."
  # TODO
  search_range = await compose_search_range(
    saved_search["subset"],
    saved_search["range_type"]
  )

  saved_search["search_terms"].append(search_range)

  if saved_search["direction"] == "oldest_first":
    saved_search["search_terms"].append("order:id")
  
  tag_str = utils.compose_tag_str(saved_search["search_terms"])

  site_url = utils.construct_tagged_url(
    POST_URL_BASE,
    tag_str
  )

  BROWSER.launch(site_url)


def test_and_prep_saved_search(saved_search: dict) -> None:
  "Runs a series of assertions to ensure the saved search provided is legal."
  assert saved_search["range_type"], "range_type not defined"

  if saved_search["range_type"] != "none":
    # asserts either favgroup or favorites
    assert saved_search["subset_type"], "subset_type not defined"
    assert saved_search["subset_type"] in ["favgroup", "favorites"], (
      "subset_type is not a valid option"
    )

    # Defines the subset, which is the search term that will be used to
    # reduce the scope of the site.
    if saved_search["subset_type"] == "favgroup":
      saved_search["subset"] = f"favgroup:{saved_search['favgroup_id']}"
    elif saved_search["subset_type"] == "favorites":
      saved_search["subset"] = f"fav:{CONFIG["username"]}"
    else:
      raise AssertionError("subset_type is not a valid option")

    # Ensures favgroup method is legal
    if saved_search["subset_type"] == "favgroup":
      try:
        saved_search["favgroup_id"] = int(saved_search["favgroup_id"])
      except KeyError:
        raise AssertionError("favgroup_id is not defined")
      except ValueError:
        raise AssertionError("favgroup_id must be an integer")
    
    # converts search_terms into a list of strings
    if "saved_terms" not in saved_search:
      saved_search["search_terms"] = []
    else:
      saved_search["search_terms"] = (
        list(saved_search["saved_terms"].split(" "))
      )
    
    # Ensures direction is legal.
    if "direction" not in saved_search:
      saved_search["direction"] = "youngest_first"
    
    assert saved_search["direction"] in [
      "youngest_first",
      "oldest_first"
    ], "direction is not defined properly."

def main() -> None:
  "E.G. python dbutil.py launch [search_tag_1] [search_tag_2]..."

  # Assert enough parameters have been provided
  assert len(sys.argv) > 2, f"Incorrect usage. Try {main.__doc__}"

  # parse the arguments
  search_search_key = sys.argv[1]
  tag_strings = sys.argv[2:]

  # select saved_search parameters
  try:
    saved_search = SAVED_SEARCHES[search_search_key]
  except KeyError:
    sys.exit(
      "The provided key is not present in config.yaml. Please check configuration or command."
    )

  # Prepare saved_search for execution
  try:
    test_and_prep_saved_search(saved_search)
  except AssertionError as e:
    sys.exit(
      f"The saved_search chosen was found, but failed with the status: {str(e)}"
    )

  # adds terms passed by parameters to the saved_terms list.
  saved_search["saved_terms"] = saved_search["saved_terms"] + tag_strings 
  
  # Launch command
  asyncio.run(process(saved_search))




if __name__ == "__main__":
  main()