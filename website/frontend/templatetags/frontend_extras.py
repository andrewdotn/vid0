from functools import cache
from html.parser import HTMLParser

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


class CssAndJsParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.css_links = []
        self.js_links = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            for (k, v) in attrs:
                if k == "src":
                    self.js_links.append(v)
        elif tag == "link":
            attr_dict = dict(attrs)

            if attr_dict.get("rel") == "stylesheet":
                self.css_links.append(attr_dict["href"])


# Could also check timestamps to determine if should re-read
@cache
def determine_build_asset_names():
    index_html = (settings.FRONTEND_DIST_DIR / "index.html").read_text()

    parser = CssAndJsParser()
    parser.feed(index_html)

    return {"css": parser.css_links, "js": parser.js_links}


@register.simple_tag()
def frontend_url():
    return settings.FRONTEND_URL


@register.simple_tag()
def frontend():
    frontend_url = settings.FRONTEND_URL
    if settings.DEBUG:
        return mark_safe(
            f"""
            <script type="module" src="{frontend_url}/@vite/client"></script>
            <link rel="stylesheet" href="{frontend_url}/style.scss">
            <script async type="module" src="{frontend_url}/index.tsx"></script>
            """
        )

    frontend_url = "/static/dist"

    def frontend_urlize(path):
        if path.startswith("/"):
            return frontend_url + path
        return f"{frontend_url}/{path}"

    assets = determine_build_asset_names()

    ret = []
    for css_link in assets["css"]:
        ret.append(f'<link rel="stylesheet" href="{frontend_urlize(css_link)}">')
    for js_link in assets["js"]:
        ret.append(
            f'<script async type="module" src="{frontend_urlize(js_link)}"></script>'
        )
    return mark_safe("\n".join(ret))
