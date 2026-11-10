# Listing Search Evaluation Bench

Evaluate a ranking with explicit candidate judgments, graded nDCG, precision, recall and reciprocal rank at a declared cutoff. The notebook compares a literal Unicode-token baseline with a baseline that also receives explicit structured filters. Per-query rankings and missed relevant identifiers remain visible, instead of hiding failures behind one average.

The synthetic English/Russian corpus has 8 fictional records, 14 authored queries and 112 explicit candidate judgments. Budget points are invented unitless numbers, not prices or currencies. These data do not describe real listings or market coverage. Equivalent language pairs share authored intent; no multilingual model was trained or evaluated.

```sh
python -m unittest -v test_search_eval
python search_eval.py --output results.json
```

The baselines do not infer bedroom limits, negation, pet rules or budgets from natural language. The structured baseline receives those constraints from the query author. Its advantage must not be reported as improved language understanding. Unknown pet policy remains unknown; it never means permission is granted. Tokenisation is NFKC plus case folding and whole Unicode word matching, without stemming or semantic retrieval.

Judgments are 0 for irrelevant, 1 for acceptable, 2 for preferred. In the metro/budget case, two-bedroom results are preferred and a three-bedroom result is acceptable; the cheaper metro case prefers the two-bedroom option over a one-bedroom option. These are explicit synthetic author preferences, not universal user preferences. The other positive cases use grade 2. No-match queries have only zero grades.

The evaluation averages answerable queries separately and reports correct empty responses on no-match queries. It defines precision as relevant results divided by k, even when fewer results are returned. It rejects duplicate ranking IDs, unjudged IDs, invalid grades and invalid cutoffs. Rank ties use stable identifier order. An explicit filter is a candidate eligibility constraint, not a source of relevance judgments.

Bring your own permitted corpus, query intents and judgments to adapt the bench. Keep evaluation judgments separate from ranker inputs; avoid training on your reported test set. This tiny authored corpus is a regression/example kit, not a representative benchmark or evidence that a search product is ready for production. No external service or telemetry is called by the evaluation code.

Maintained by [NovAsia Estate](https://novasia.estate/). [Source and issues](https://github.com/novasia-estate/open-property-lab/tree/main/listing-search-evaluation). MIT.
