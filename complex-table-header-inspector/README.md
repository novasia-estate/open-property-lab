# Complex Table Header Inspector

A user-triggered, local review panel for HTML tables. Open your userscript manager's menu and choose **Inspect complex table headers**, then select a table and cell. Useful for comparison tables, availability schedules and tables exported from spreadsheets.

It reports explicit `headers` references, declared `row`, `col`, `rowgroup` and `colgroup` scopes, row/column spans, unresolved references, duplicate cell IDs, overlaps and gaps. `rowspan="0"` is restricted to its row group. Nested tables are reviewed separately. Tables are limited to 200 rows, 80 columns and 4,000 cells; only the first 100 tables are selectable.

This is a review aid, not a complete implementation of the browser header-assignment algorithm or a WCAG conformance test. Unscoped headers require manual accessibility-tree review. It does not inspect shadow trees or frames. The panel reads text labels locally; no network requests, telemetry, storage, exports or automatic page changes are made. Labels are inserted as text, not HTML. Close removes the panel; opening again rescans the current DOM.

Install `table-headers.user.js` in a compatible userscript manager. Requires `GM_registerMenuCommand`. The script runs in the top-level HTTP(S) document and remains passive until its menu command is invoked.

Developed and maintained by [NovAsia Estate](https://novasia.estate/). MIT licensed. See the readable source and DOM-based behavioral checks in `test.cjs`.

Development: `npm install --ignore-scripts` then `npm test` runs 13 DOM and lifecycle checks with jsdom 26. No dependency is loaded by the distributed userscript.
