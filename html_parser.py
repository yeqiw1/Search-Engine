# html_parser.py
from urllib.parse import urldefrag, urljoin
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

def _safe_join_text(nodes):
    parts = []
    for n in nodes:
        try:
            t = n.get_text(separator=" ", strip=True)
            if t:
                parts.append(t)
        except Exception:
            continue
    return " ".join(parts)


def extract_page_data(html, base_url=""):
    """
    Extract structured information from a page.

    Returns a dict with:
      title, h1, h2, h3, bold, body, anchors, links

    - anchors: concatenated anchor text from all hyperlinks on the page
    - links: normalized outlinks resolved against base_url, without fragments
    """
    fields = {
        "title": "",
        "h1": "",
        "h2": "",
        "h3": "",
        "bold": "",
        "body": "",
        "anchors": "",
        "links": [],
    }

    try:
        soup = BeautifulSoup(html, "lxml")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        if soup.title and soup.title.string:
            fields["title"] = soup.title.string.strip()

        fields["h1"] = _safe_join_text(soup.find_all("h1"))
        fields["h2"] = _safe_join_text(soup.find_all("h2"))
        fields["h3"] = _safe_join_text(soup.find_all("h3"))
        fields["bold"] = _safe_join_text(soup.find_all(["b", "strong"]))
        fields["body"] = soup.get_text(separator=" ", strip=True)

        anchor_text_parts = []
        links = []
        for a in soup.find_all("a"):
            try:
                anchor_text = a.get_text(separator=" ", strip=True)
                if anchor_text:
                    anchor_text_parts.append(anchor_text)

                href = a.get("href")
                if not href:
                    continue

                normalized = urljoin(base_url, href)
                normalized, _ = urldefrag(normalized)
                if normalized:
                    links.append(normalized)
            except Exception:
                continue

        fields["anchors"] = " ".join(anchor_text_parts)
        fields["links"] = links
        return fields

    except Exception:
        return fields
