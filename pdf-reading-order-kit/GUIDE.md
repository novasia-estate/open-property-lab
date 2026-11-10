# When PDF extraction attaches the right price to the wrong card

A brochure importer can recover every digit correctly and still create incorrect records. The missing piece is the relationship between the reference, the area and the price. Three lists with equal lengths do not prove that their first entries describe the same object.

This worked investigation includes seven synthetic PDF fixtures, explicit annotations, runnable baselines and thirteen tests that read actual generated PDFs. All references and numbers are invented. No currency, offer or real market observation is implied.

## A small failure you can reproduce

The first page contains three framed cards:

| Reference | Area token | Price token |
| --- | ---: | ---: |
| A101 | 41.00 | 2100000 |
| B202 | 52.00 | 3200000 |
| C303 | 63.00 | 4300000 |

The ordered control writes each card's text together. A second PDF keeps the three cards in the same visual positions, but writes price text into the PDF content stream in reverse order. PDF extraction using `use_text_flow=True` exposes the changed order.

A simple importer collects references, areas and prices independently, then zips the lists. It now assigns `4300000` to A101 and `2100000` to C303. B202 happens to stay correct. All three reference, area and price counts still match. No digit is missing or corrupted, so a numerical validity check alone does not catch the association error.

This is a deliberately limited baseline. It already refuses unequal counts and repeated unscoped references, yet the same-count permutations still fail. It is included to help recognise and reproduce the failure, rather than as an importer to adopt.

## Run the investigation

Open the [complete source and fixtures](https://github.com/novasia-estate/open-property-lab/tree/main/pdf-reading-order-kit), download the folder and use Python 3.11 or newer:

```sh
cd pdf-reading-order-kit
python -m pip install -r requirements.txt
python -m unittest -v test_reading_order
python reading_order.py --output results.json
```

The PDFs are checked in, so regeneration is optional. `python build_fixtures.py` rebuilds the same fixtures with ReportLab's deterministic mode. The separate annotation manifest records expected associations; the evaluator compares against them after extraction.

## Measured results on these fixtures

| Fixture | Global-list result | Correct global associations | Reviewed-region decisions matching annotations |
| --- | --- | ---: | ---: |
| Ordered control | Associated | 3 of 3 | 3 of 3 |
| Reverse price stream | Associated | 1 of 3 | 3 of 3 |
| Reverse area stream | Associated | 1 of 3 | 3 of 3 |
| Mixed area and price streams | Associated | 0 of 3 | 3 of 3 |
| Extra footer fields | Abstained: unequal counts | No associations emitted | 3 of 3 |
| Repeated reference across pages | Abstained: unscoped duplicate | No associations emitted | 4 of 4 |
| Two area fields inside one card | Abstained: unequal counts | No associations emitted | 3 of 3, including one abstention |

These are results on deliberately selected synthetic cases. They do not estimate accuracy on real brochures. A correct abstention means the system refused to choose between conflicting values; it does not mean that it recovered a usable record.

## What the region comparison actually does

The second baseline receives explicitly reviewed page regions. It examines recognised tokens inside each box and emits a record only when exactly one reference, one area and one price occur there. Missing or duplicate fields and words crossing a region boundary cause abstention. Invalid, overlapping and out-of-page regions are rejected.

The detector receives boxes and page numbers, without the expected field values. The evaluator alone reads the expected values. This separation makes the comparison reproducible, but the reviewed boxes still make the task substantially easier: automatic card discovery and region annotation quality are outside this experiment.

Each output retains a region identifier, a one-based page number, a bounding box and the source file's SHA-256. Region coordinates are PDF points in `(x0, top, x1, bottom)` order. The reference label is not treated as a globally unique identifier; the same A101 label on another page remains a separate region-scoped observation.

The [full machine-readable results](https://github.com/novasia-estate/open-property-lab/blob/main/pdf-reading-order-kit/results.json) include the actual wrong tuples as well as correct outputs. The [fixture manifest](https://github.com/novasia-estate/open-property-lab/blob/main/pdf-reading-order-kit/fixtures/manifest.json) contains the annotations and links each case to its PDF.

## Use it as an importer regression check

1. Keep the original PDF and record its hash before review. A corrected export should retain a reference to that exact source.
2. Review relationships at the card or row level. Checking that every extracted number appears somewhere on the page is insufficient.
3. Preserve page and region scope when labels repeat. Do not silently overwrite the first observation with the last one.
4. Require an explicit unresolved state for conflicting fields. A plausible first value is still an arbitrary choice.
5. Add representative documents from your own permitted corpus. Include layouts that fail, and keep those failures in the regression set.
6. Record human corrections separately from original extraction. A regression report should distinguish correct extraction, corrected extraction and abstention.

The test suite includes positive controls and deliberate failures: it checks the exact wrong associations, successful region-scoped associations, duplicate-label abstention, ambiguous-field abstention, boundary handling and invalid boxes. Passing this small kit does not establish that an importer is ready for unattended production use.

## Scope and references

The tokens use a narrow grammar (`REF:`, `AREA:` and `PRICE:`) chosen to isolate association errors. There is no OCR, multilingual layout discovery, currency conversion or inference about actual availability. The fixtures are not tagged-PDF accessibility tests, and this experiment does not repair reading order for assistive technology.

The [pdfplumber documentation](https://github.com/jsvine/pdfplumber#extracting-text) explains word extraction and its text-flow option. [W3C's PDF3 technique](https://www.w3.org/WAI/WCAG22/Techniques/pdf/PDF3) discusses the separate issue of meaningful reading and navigation order in tagged documents. These are different concerns; this kit tests field associations in extracted data.

Prepared by [NovAsia Estate](https://novasia.estate/). Code, fixtures and documentation are released under the MIT license.
