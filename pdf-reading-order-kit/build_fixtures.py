"""Generate wholly synthetic PDFs and a separate annotation manifest."""
import json
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas

ROOT = Path(__file__).parent
CARDS = [('A101', '41.00', '2100000'), ('B202', '52.00', '3200000'), ('C303', '63.00', '4300000')]
CASES = ['ordered', 'reverse-price-stream', 'reverse-area-stream', 'mixed-stream',
         'distractor-footer', 'repeated-ref-across-pages', 'ambiguous-area']


def build(root=ROOT):
    target = Path(root) / 'fixtures'
    target.mkdir(parents=True, exist_ok=True)
    manifest = []
    for name in CASES:
        c = Canvas(str(target / (name + '.pdf')), pagesize=(600, 600), invariant=1)
        c.setTitle('Synthetic field association fixture: ' + name)
        c.setAuthor('Open Property Lab')
        regions, expected = [], []
        page_count = 2 if name == 'repeated-ref-across-pages' else 1
        for page in range(1, page_count + 1):
            c.setFont('Helvetica-Bold', 17)
            c.drawString(30, 558, 'Synthetic property cards')
            c.setFont('Helvetica', 10)
            c.drawString(30, 536, 'Not listings, offers or market prices. Experiment: ' + name)
            cards = CARDS if page == 1 else [('A101', '74.00', '5400000')]
            for i, card in enumerate(cards):
                x = 40 + 185 * i
                c.setStrokeColorRGB(.2, .35, .5)
                c.rect(x - 10, 375, 160, 100)
                key = f'p{page}-card{i+1}'
                regions.append({'key': key, 'page': page, 'bbox': [x-10, 125, x+150, 225]})
                truth = {'key': key, 'status': 'associated', 'fields': dict(zip(('ref', 'area', 'price'), card))}
                if name == 'ambiguous-area' and i == 0:
                    truth = {'key': key, 'status': 'abstain'}
                expected.append(truth)
            c.setFont('Helvetica', 11)
            orders = [list(range(len(cards))) for _ in range(3)]
            if name == 'reverse-price-stream': orders[2].reverse()
            if name == 'reverse-area-stream': orders[1].reverse()
            if name == 'mixed-stream': orders[1], orders[2] = [2,0,1], [1,2,0]
            # Drawing coordinates stay constant, only PDF operator order changes.
            stream = [(i, j) for i in range(len(cards)) for j in range(3)] if name == 'ordered' else [(i, j) for j in range(3) for i in orders[j]]
            for i, j in stream:
                c.drawString(40+185*i, 450-25*j, ('REF:', 'AREA:', 'PRICE:')[j] + cards[i][j])
            if name == 'ambiguous-area': c.drawString(40, 385, 'AREA:99.00')
            if name == 'distractor-footer': c.drawString(30, 65, 'AREA:999.00 PRICE:9999999')
            c.setFont('Helvetica', 9)
            c.drawString(30, 40, f'Page {page}; coordinates use PDF points. Deliberately synthetic.')
            c.showPage()
        c.save()
        manifest.append({'name': name, 'file': name+'.pdf', 'regions': regions, 'expected': expected})
    (target / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    print(f'Built {len(build())} synthetic fixtures.')
