# Tourism Recovery Gap Lab

Annual international-arrivals series,2000–2025, with missing data preserved and2019 used as an explicit common-year reference. UN Tourism data distributed by World Bank WDI. Arrivals count trips, not unique people; country collection methods differ. Annual observations cannot demonstrate monthly seasonality or rental occupancy.

## Reproduce and inspect

- `arrivals.csv` is the publication input with original observations and explicit derived fields.
- `provenance.json` records retrieval, exact source URLs and definitions.
- Source snapshots are cached for reproducibility; refreshing upstream data creates a new revision rather than silently changing these results.
- `python -B validate.py` checks the local release without network calls.

This package contains no invented observations or source claims. Preserve missing values; a missing observation is never zero. Use the original units before interpreting an index. Licensed analysis code: MIT; underlying World Bank/UN/IMF/OpenStreetMap data remain governed by the named sources' terms. No ownership of those sources is claimed.

Prepared by [NovAsia Estate](https://novasia.estate/). [Source and methodology](https://github.com/novasia-estate/open-property-lab/tree/main/tourism-recovery-gap-lab). These are contextual research materials, not evidence that any property is available or an investment recommendation.
