# Brochure Table Recovery Workbench

An explicit review workflow for a public digital PDF: locate ruled tables, keep source page and bounding box, correct text without erasing original cells, then download spreadsheet-safe CSV, JSON provenance or a ZIP containing both. A recovered value is not authenticated inventory, a current price or an availability claim.

## Run

Python3.10+: `pip install -r requirements.txt`; `streamlit run app.py`. `python -B -m unittest -q` checks exports, edit provenance, invalid inputs and (with optional reportlab installed) actual digital-PDF extraction. The synthetic fixture has one ruled table with an invented unit reference and area, not a market listing.

Limits:10MiB/PDF,30pages,100tables,25000cells. No OCR, free-text table reconstruction, inferred headers, price conversion or guessed missing fields. Inspection errors fail before export. The parser is not a security sandbox; use known public brochures or synthetic test files.

## Privacy and export semantics

The hosted app sends uploads to the Streamlit server. It is not an offline or confidential-document service. Application code processes uploaded bytes in session memory, has no external API calls and intentionally does not write the source PDF to disk; the hosting provider controls infrastructure and logs. Do not upload personal or confidential documents. Clear the session when finished.

CSV adds a leading apostrophe to formula-looking cell text for spreadsheet safety. JSON retains the original text and a separate edited copy, the SHA-256 of source bytes, inspected pages and table bounding box. The source PDF is not included in the output ZIP. Row1 remains data; the app does not pretend to know whether it is a header.

Maintained by [NovAsia Estate](https://novasia.estate/). [Source and issues](https://github.com/novasia-estate/open-property-lab/tree/main/brochure-table-recovery). MIT. pdfplumber and other dependencies retain their own licenses.
