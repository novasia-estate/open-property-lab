# Currency Context Atlas

Official annual-average local currency units per US dollar,2000–2025. The IMF series is distributed by World Bank WDI. The common-year2019=100 index describes exchange-rate change, not a property return, executable FX quote or investment forecast. A higher index means more local units per dollar.

## Reproduce and inspect

- `exchange-rates.csv` is the publication input with original observations and explicit derived fields.
- `provenance.json` records retrieval, exact source URLs and definitions.
- Source snapshots are cached for reproducibility; refreshing upstream data creates a new revision rather than silently changing these results.
- `python -B validate.py` checks the local release without network calls.

This package contains no invented observations or source claims. Preserve missing values; a missing observation is never zero. Use the original units before interpreting an index. Licensed analysis code: MIT; underlying World Bank/UN/IMF/OpenStreetMap data remain governed by the named sources' terms. No ownership of those sources is claimed.

Prepared by [NovAsia Estate](https://novasia.estate/). [Source and methodology](https://github.com/novasia-estate/open-property-lab/tree/main/currency-context-atlas). These are contextual research materials, not evidence that any property is available or an investment recommendation.
