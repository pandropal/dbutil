from requests.auth import HTTPBasicAuth
from requests import get, Response, exceptions
from urllib.parse import urlparse, urlencode, urlunparse

def fetch(url: str, auth: HTTPBasicAuth) -> Response:
  try:
    response = get(
      url=url,
      auth=auth,
      headers={ 
        'User-Agent': 'My User Agent 1.0' # Required for searching danbooru.
      }
    )
    response.raise_for_status()
  except exceptions.RequestException as e:
    raise e

def compose_tag_str(*tags:list[str]) -> str:
  "Combines multiple tags into a single tag string"
  tags = list(tags)
  return " ".join(tags)

def construct_url(base_url: str, query_params: dict) -> str:
  "When given a base URL, returns the url with an attached query string"
  base_parsed = urlparse(base_url)
  constructed_query = urlencode(query_params, doseq=True)
  new_url = urlunparse((
    base_parsed.scheme,
    base_parsed.netloc,
    base_parsed.path,
    base_parsed.params,
    constructed_query,
    base_parsed.fragment
  ))

  return new_url

def construct_tagged_url(base_url: str, tag_str: str) -> str:
  """
  When given a base URL and a tag query, returns a url with query string
  tag_str should be space delimited, E.G. "tag1 tag2 tag3"
  """
  query_params = {
    "tags": [tag_str]
  }

  return construct_url(base_url, query_params)