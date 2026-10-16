from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, parse_qs


class Parser(HTMLParser):
    def __init__(self, base):
        super().__init__()
        self.base = base
        self.links = set()
        self.forms = []
        self._form = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            href = a["href"].split("#")[0]
            if href and not href.startswith(("javascript:", "mailto:")):
                self.links.add(urljoin(self.base, href))
        if tag == "form":
            self._form = {
                "action": urljoin(self.base, a.get("action") or self.base),
                "method": (a.get("method") or "get").lower(),
                "fields": {},
            }
        if tag == "input" and self._form is not None and a.get("name"):
            self._form["fields"][a["name"]] = a.get("value", "1") or "1"

    def handle_endtag(self, tag):
        if tag == "form" and self._form is not None:
            self.forms.append(self._form)
            self._form = None


def same_host(a, b):
    return urlparse(a).netloc == urlparse(b).netloc


def discover(page_url, html):
    p = Parser(page_url)
    try:
        p.feed(html)
    except Exception:
        pass
    links_params = [u for u in p.links if same_host(page_url, u) and parse_qs(urlparse(u).query)]
    get_forms = [f for f in p.forms if f["method"] == "get" and f["fields"]]
    post_forms = [f for f in p.forms if f["method"] == "post" and f["fields"]]
    return {"links": sorted(set(links_params)), "get_forms": get_forms, "post_forms": post_forms}


def path_targets(url):
    parts = urlparse(url)
    segs = parts.path.strip("/").split("/")
    out = []
    for i, s in enumerate(segs):
        if s.isdigit():
            out.append((i, s))
    return out
