"""Small, disclosed baselines for synthetic PDF field-association experiments.

No layout discovery, OCR, tagged-PDF accessibility assessment or market data.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
from pathlib import Path
import pdfplumber

FIELDS = {
    'ref': re.compile(r'REF:([A-Z][A-Z0-9-]*)\Z'),
    'area': re.compile(r'AREA:([0-9]+\.[0-9]{2})\Z'),
    'price': re.compile(r'PRICE:([0-9]+)\Z'),
}


def field(word):
    for name, pattern in FIELDS.items():
        m = pattern.fullmatch(word['text'])
        if m:
            return name, m.group(1)
    return None


def validate_regions(regions, pages):
    seen = set()
    for region in regions:
        page, key, box = region['page'], region['key'], region['bbox']
        if type(page) is not int or page not in pages or not isinstance(key, str) or not key:
            raise ValueError('Invalid page or region identifier')
        if key in seen:
            raise ValueError('Region identifiers must be unique')
        seen.add(key)
        if len(box) != 4 or any(type(x) not in (int, float) or not math.isfinite(x) for x in box):
            raise ValueError('Invalid bounding box')
        x0, top, x1, bottom = box
        width, height = pages[page]
        if not (0 <= x0 < x1 <= width and 0 <= top < bottom <= height):
            raise ValueError('Bounding box outside page')
    for i, a in enumerate(regions):
        for b in regions[i+1:]:
            if a['page'] == b['page'] and intersects(a['bbox'], b['bbox']):
                raise ValueError('Regions must not overlap')


def intersects(a, b):
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])


def global_lists(words):
    """A deliberately limited baseline: independently collected lists, then zip.

    Refuses unequal counts/duplicate labels. Even these guards cannot detect
    same-count permutations between columns. Not a recommended importer.
    """
    values = {k: [] for k in FIELDS}
    for word in words:
        token = field(word)
        if token:
            values[token[0]].append(token[1])
    if not values['ref'] or len({len(v) for v in values.values()}) != 1:
        return {'status': 'abstain', 'reason': 'unequal_or_empty_counts', 'rows': []}
    if len(set(values['ref'])) != len(values['ref']):
        return {'status': 'abstain', 'reason': 'repeated_unscoped_ref', 'rows': []}
    return {'status': 'associated', 'rows': [dict(zip(FIELDS, row)) for row in zip(*values.values())]}


def scoped_regions(words, regions, pages):
    """Uses supplied reviewed regions, never ground-truth field values."""
    validate_regions(regions, pages)
    results = []
    for region in regions:
        box = region['bbox']
        tokens = {k: [] for k in FIELDS}
        boundary = False
        for word in words:
            if word['page'] != region['page']:
                continue
            wb = [word['x0'], word['top'], word['x1'], word['bottom']]
            token = field(word)
            if token and intersects(box, wb):
                if not (box[0] <= wb[0] and box[1] <= wb[1] and wb[2] <= box[2] and wb[3] <= box[3]):
                    boundary = True
                tokens[token[0]].append(token[1])
        item = {'key': region['key'], 'page': region['page'], 'bbox': box}
        if boundary or any(len(v) != 1 for v in tokens.values()):
            item.update(status='abstain', reason='boundary_or_ambiguous_fields')
        else:
            item.update(status='associated', fields={k: v[0] for k, v in tokens.items()})
        results.append(item)
    return results


def inspect_pdf(path, regions):
    path = Path(path)
    if path.stat().st_size > 1024 * 1024:
        raise ValueError('Fixture tool limit: 1 MiB')
    words, pages = [], {}
    with pdfplumber.open(path) as pdf:
        if len(pdf.pages) > 10:
            raise ValueError('Fixture tool limit: ten pages')
        for number, page in enumerate(pdf.pages, 1):
            pages[number] = (page.width, page.height)
            for w in page.extract_words(use_text_flow=True):
                words.append({k: w[k] for k in ('text', 'x0', 'top', 'x1', 'bottom')} | {'page': number})
    return {'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'word_count': len(words), 'global_lists': global_lists(words),
            'reviewed_regions': scoped_regions(words, regions, pages)}


def evaluate(root):
    root = Path(root)
    manifest = json.loads((root / 'fixtures/manifest.json').read_text())
    reports = []
    for case in manifest:
        result = inspect_pdf(root / 'fixtures' / case['file'], case['regions'])
        truth = case['expected']
        expected_rows = [x['fields'] for x in truth if x['status'] == 'associated']
        guessed = result['global_lists']['rows']
        # Tuple equality keeps the price attached to its original ref and area.
        correct = sum(any(row == expected for expected in expected_rows) for row in guessed)
        region_correct = sum(got['status'] == expected['status'] and
                             (got['status'] != 'associated' or got['fields'] == expected['fields'])
                             for got, expected in zip(result['reviewed_regions'], truth))
        reports.append({'case': case['name'], 'expected_regions': len(truth),
                        'global_status': result['global_lists']['status'],
                        'global_associated': len(guessed), 'global_correct_associations': correct,
                        'region_decisions_correct': region_correct, 'details': result})
    return {'scope': 'Seven synthetic fixtures, explicit reviewed boxes; not real-world accuracy.', 'cases': reports}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default=str(Path(__file__).parent))
    parser.add_argument('--output')
    args = parser.parse_args()
    text = json.dumps(evaluate(args.root), indent=2) + '\n'
    if args.output:
        Path(args.output).write_text(text, encoding='utf-8')
    else:
        print(text, end='')
