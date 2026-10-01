#!/usr/bin/env python3
"""Capture static source text; explicitly not a rendered-page crawler."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlparse
from urllib.request import Request, urlopen

def normalize(text):
    return re.sub(r'\s+', ' ', text).strip()

class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hidden = 0
        self.chunks = []
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'noscript', 'template'):
            self.hidden += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'noscript', 'template'):
            self.hidden = max(0, self.hidden - 1)
    def handle_data(self, text):
        if not self.hidden:
            self.chunks.append(text)

def capture(source):
    if urlparse(source).scheme in ('https', 'http'):
        request = Request(source, headers={'User-Agent': 'Akapulu-FAQ-source-review/1.0'})
        with urlopen(request, timeout=30) as response:
            content_type = response.headers.get_content_type()
            if content_type not in ('text/html', 'text/plain'):
                raise ValueError(f'Unsupported source type: {content_type}')
            raw = response.read(2_000_001)
            if len(raw) > 2_000_000:
                raise ValueError('Page exceeds capture limit; choose a smaller relevant page.')
            html = raw.decode(response.headers.get_content_charset() or 'utf-8')
            source = response.url
    else:
        path = Path(source).expanduser().resolve()
        html = path.read_text(encoding='utf-8')
        content_type = 'text/html'
        source = str(path)
    if content_type == 'text/html':
        parser = VisibleText()
        parser.feed(html)
        text = normalize(' '.join(parser.chunks))
    else:
        text = normalize(html)
    if len(text) < 120:
        raise ValueError('Too little static content; inspect rendered content or request the page text.')
    return {'source': source, 'captured_at': datetime.now(timezone.utc).isoformat(),
            'method': 'static HTML/text extraction; human relevance review required',
            'text': text, 'sha256': sha256(text.encode()).hexdigest()}

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source')
    p.add_argument('--out', required=True)
    args = p.parse_args()
    try:
        data = capture(args.source)
        dest = Path(args.out)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open('x', encoding='utf-8') as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write('\n')
        print(f'Captured {len(data["text"])} characters to {dest}. Review page relevance before use.')
    except (OSError, ValueError) as exc:
        p.exit(1, f'Capture failed: {exc}\n')
