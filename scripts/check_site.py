#!/usr/bin/env python3
"""Check the local or deployed portfolio and all its original report figures."""
import argparse
import base64
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import urlopen, Request

ROOT = Path(__file__).resolve().parents[1]

class Document(HTMLParser):
    def __init__(self, data):
        super().__init__()
        self.ids, self.links, self.images = set(), [], []
        self.feed(data.decode('utf-8'))

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.add(a['id'])
        for key in ('src', 'href', 'poster'):
            if a.get(key):
                self.links.append(a[key])
        if tag == 'img':
            self.images.append(a.get('src', ''))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base-url', help='Check the deployed GitHub Pages project URL instead of disk.')
    args = ap.parse_args()
    cache = {}
    def read(path):
        if path not in cache:
            if args.base_url:
                request = Request(urljoin(args.base_url.rstrip('/')+'/', path), headers={'User-Agent':'PortfolioAssetCheck/1.0','Cache-Control':'no-cache'})
                with urlopen(request, timeout=45) as response:
                    cache[path] = response.read()
            else:
                cache[path] = (ROOT / path).read_bytes()
        return cache[path]
    docs = {name: Document(read(name)) for name in ['index.html', 'elective_wait_times.html']}
    for name, doc in docs.items():
        for link in doc.links:
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc:
                continue
            assert not parsed.path.startswith('/'), f'Root-relative project link: {link}'
            target = unquote(parsed.path) or name
            if target == './':
                target = 'index.html'
            data = read(target)
            if parsed.fragment and target.endswith('.html'):
                target_doc = docs.get(target) or Document(data)
                assert unquote(parsed.fragment) in target_doc.ids, f'Missing section: {link}'
            if target.endswith('.png'):
                assert data.startswith(b'\x89PNG\r\n\x1a\n'), f'Not a PNG: {target}'
    manifest = json.loads(read('assets/figures.json'))
    report_images = docs['elective_wait_times.html'].images
    assert len(report_images) == len(manifest) == 16, 'Expected all 16 original report figures'
    for img, item in zip(report_images, manifest):
        assert img.startswith('data:image/png;base64,'), 'Report must remain self-contained'
        original = base64.b64decode(img.split(',', 1)[1], validate=True)
        exported = read(item['path'])
        assert original == exported, f'Figure differs from original: {item["path"]}'
        assert hashlib.sha256(exported).hexdigest() == item['sha256']
        assert item['section'] in docs['elective_wait_times.html'].ids
    assert set(docs['index.html'].images) == {f['path'] for f in manifest}, 'Homepage must expose all original figures'
    print(f'PASS: {len(cache)} resources; all relative links and report anchors; 16/16 report images and 16/16 exported figures verified byte-for-byte.')
    print('Target:', args.base_url or ROOT)

if __name__ == '__main__':
    main()
