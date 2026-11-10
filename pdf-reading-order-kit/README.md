# PDF Field Association Test Kit

Seven small synthetic PDFs expose a specific importer failure: collecting references, areas and prices into three independent lists and joining them by position can attach a valid number to the wrong property card. Matching counts do not establish a relationship.

The executable regression kit includes a positive control, deliberately reordered PDF content streams, footer distractors, repeated labels across pages and an ambiguous field. Every expected association is explicitly annotated.

## Reproduce

Python 3.11 or newer:

```sh
python -m pip install -r requirements.txt
python -m unittest -v test_reading_order
python reading_order.py --output results.json
```

The checked-in `fixtures/` directory includes PDFs and the annotation manifest. `python build_fixtures.py` recreates it with ReportLab's deterministic mode. Expected values are only used by the evaluator, after the two baselines have run. The scoped baseline receives reviewed page regions, not expected cell values.

## What is measured

An association is correct only when the complete `(reference, area, price)` tuple matches its original card. The global-list baseline refuses unequal field counts and repeated unscoped references. Nevertheless, same-count permutations still produce wrong associations. The second baseline uses explicitly supplied, non-overlapping regions and abstains on missing, duplicate or boundary-crossing fields.

No aggregate accuracy claim is made. Seven intentionally selected synthetic cases are neither a representative market sample nor a real-brochure benchmark. Manually supplying the card regions makes the scoped task much easier. Discovering those regions is explicitly outside this experiment.

The full method, measured case results and an adoption checklist are in [GUIDE.md](GUIDE.md). [results.json](results.json) retains each source SHA-256, page, box and baseline output. The test suite regenerates and reads actual PDFs; it also checks abstention and invalid region handling.

## Limits

The token grammar is deliberately narrow, with invented integer prices and decimal areas and no asserted currency. There is no OCR, multilingual layout discovery, currency conversion, tagged-PDF repair or accessibility certification. The library is a bounded test harness for trusted synthetic inputs, not a hardened parser for arbitrary hostile PDFs. A result that passes this kit may still fail on real documents.

Maintained by [NovAsia Estate](https://novasia.estate/). Source, examples and issues: [Open Property Lab](https://github.com/novasia-estate/open-property-lab/tree/main/pdf-reading-order-kit). MIT.
