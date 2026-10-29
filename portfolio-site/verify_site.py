"""Check the staged static portfolio before deployment.

This validates structure and project links without making network requests.
"""
from html.parser import HTMLParser
from pathlib import Path

BASE = Path(__file__).resolve().parent


class SiteCheck(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.anchors = set()
        self.local_links = []
        self.heading_count = 0

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if attr.get('id'):
            self.anchors.add(attr['id'])
        if tag == 'a':
            url = attr.get('href', '')
            if url.startswith('#'):
                self.local_links.append(url[1:])
        if tag == 'h1':
            self.heading_count += 1


def run():
    html = (BASE / 'index.html').read_text(encoding='utf-8')
    styles = (BASE / 'styles.css').read_text(encoding='utf-8')
    js = (BASE / 'script.js').read_text(encoding='utf-8')
    assert 'nexusdesk-demo.onrender.com/demo/' in html
    assert 'github.com/eddy235/NexusDesk' in html
    assert 'securescan-demo.onrender.com/' in html
    for label in ('Kenya National Library Service Website', 'Mint Dental Centre Website',
                  'TryHackMe Cyber Lab', 'Packet Defender',
                  'id="experience"', 'id="certifications"', 'id="contact"'):
        assert label in html, f'Missing preserved section: {label}'
    parser = SiteCheck()
    parser.feed(html)
    missing = [name for name in parser.local_links if name and name not in parser.anchors]
    assert not missing, f'Broken page anchors: {missing}'
    assert parser.heading_count == 1, 'Page must have exactly one h1'
    assert len(styles) > 2000 and '.project-card' in styles
    assert "nav-toggle" in js
    assert '<script src="script.js"></script>' in html
    assert 'href="styles.css"' in html
    print('PASS: staged portfolio source, links, navigation and project content')


if __name__ == '__main__':
    run()
