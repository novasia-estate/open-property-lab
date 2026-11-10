# Listing Accessibility Inspector

Review open HTML files in a VS Code-compatible editor before publishing property cards or enquiry forms. Diagnostics point to original source locations: missing image alternatives, unnamed links/buttons, unlabelled controls, broken ARIA label references, duplicate IDs and full documents missing a language declaration.

Install the VSIX, open an HTML file and run **Listing Accessibility: Inspect Active HTML**. Open HTML documents are checked after edits. `listingAccessibility.enabled` disables checks. It does not crawl the workspace, call a network service, run shell commands or save your files. No telemetry is added by this extension.

The parser is parse5, not a regex imitation of HTML. Meaningful alternatives and visual order still require human judgement. Empty `alt` is accepted for decorative images; the extension never fills it automatically to hide a problem. Labels are checked using a disclosed subset of HTML/ARIA naming rules. CSS visibility, JavaScript-generated DOM, shadow DOM, computed accessibility trees, contrast and screen-reader behavior are not evaluated. **A clean result is not WCAG conformance or a legal accessibility certificate.**

## Development

`npm ci --ignore-scripts` then `npm test`. Tests include valid/broken cards, labels and references, fragments, comments, hidden content, Unicode offsets and inspection limits. Third-party parser licenses are retained in the packaged dependencies.

Maintained by [NovAsia Estate](https://novasia.estate/). [Source and issues](https://github.com/novasia-estate/open-property-lab/tree/main/listing-accessibility-inspector). MIT. No advertising or commercial-keyword link blocks.
