#!/usr/bin/env python3
"""Copy original PNGs from the self-contained report; never execute analysis."""
import base64
import hashlib
import json
import struct
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ['10-1', '11-1', '12-1', '14-1', '15-1', '17-1', '18-1',
          '20-1', '21-1', '23-1', '24-1', '25-1', '26-1', '26-2', '33-1', '34-1']


class Figures(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sections = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'section':
            self.sections.append(attrs.get('id', ''))
        if tag == 'img':
            self.images.append((attrs['src'], self.sections[-1]))

    def handle_endtag(self, tag):
        if tag == 'section':
            self.sections.pop()


def main():
    parser = Figures()
    parser.feed((ROOT / 'elective_wait_times.html').read_text())
    if len(parser.images) != len(CHUNKS):
        raise SystemExit('Figure count changed: review the original chunk-to-figure mapping before exporting.')
    manifest = []
    for chunk, (src, section) in zip(CHUNKS, parser.images):
        relative = f'elective_wait_times_files/figure-html/unnamed-chunk-{chunk}.png'
        if not src.startswith('data:image/png;base64,'):
            raise SystemExit('Expected an embedded original PNG; report was not changed.')
        data = base64.b64decode(src.split(',', 1)[1], validate=True)
        if data[:8] != b'\x89PNG\r\n\x1a\n':
            raise SystemExit('Invalid PNG data')
        destination = ROOT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        width, height = struct.unpack('>II', data[16:24])
        manifest.append(dict(path=relative, section=section, width=width, height=height,
                             sha256=hashlib.sha256(data).hexdigest()))
    (ROOT / 'assets/figures.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Exported {len(manifest)} original figures without changing the report or statistical results.')


if __name__ == '__main__':
    main()
