"""Search handoff: review the query results and import chosen source pages."""
from urllib.parse import urlencode

def search_url(search_term):
    if not isinstance(search_term, str) or not 1 <= len(search_term.strip()) <= 500:
        raise ValueError("Enter a search query between 1 and 500 characters.")
    return "https://www.google.com/search?" + urlencode({"q": search_term.strip()})
