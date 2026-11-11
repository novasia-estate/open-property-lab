# Focal Crop Review Lab

An offline-capable browser workbench for reviewing the effect of common media aspect ratios on user-annotated regions. Open `index.html` locally or use the published interactive page. No server, build step or runtime dependency is required.

Load a JPEG/PNG/WebP or use the synthetic room diagram. Mark up to 12 regions by dragging or entering pixel coordinates. Compare square, 4:3, 3:2 and 16:9 crop proposals, inspect per-region retained area, export a provenance-bound JSON plan or a rendered PNG.

The candidate search is disclosed in the UI: for the largest source window of a chosen aspect ratio, consider source edges/centre and region edges/centres. Maximise the smallest retained-area fraction, then the average, then prefer the centre. This is a finite search, not a global-optimality claim. Clipping remains explicitly visible. With no regions the crop is centred.

Local inputs: at most 8 MiB and 16 million decoded pixels. Browser decoding occurs before the dimension check; do not open untrusted decompression bombs. No subject recognition, remote upload, analytics or persistence is implemented by the tool. Host analytics are outside its scope. JSON omits filename and includes source SHA-256 when available; demo sources are identified separately. PNG is re-rendered without annotations and capped at 1600px; it is not a certified anonymisation operation.

Run `npm install --ignore-scripts` then `npm test`. Fourteen checks cover geometry, invalid input, bounded deterministic proposals and the actual DOM demo/add/remove/clear/export lifecycle. The canvas mocks in the DOM test verify calls; the hosted browser workflow separately verifies real pixel rendering/downloads.

Developed by [NovAsia Estate](https://novasia.estate/). MIT licensed.
