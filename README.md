# Open Property Lab

Useful, bounded tools and reproducible research for property-data teams. Each directory is a distinct project with its own README, examples, limitations and checks. Maintained by [NovAsia Estate](https://novasia.estate/).

## Tools

| Project | User workflow |
| --- | --- |
| [Service Charge Allocation](novasia-service-charge-allocation) | Reconcile quoted shared expenses to exact minor currency units with explicit weights and auditable largest remainders. |
| [Listing Redirect Planner](listing-redirect-planner) | Review URL migration graphs and guarded Nginx snippets without changing a server. |
| [Listing Accessibility Inspector](listing-accessibility-inspector) | Source-located diagnostics in an actual VS Code-compatible editor; no automatic compliance claims. |
| [Property Area Ranges](property-area-ranges) | Preserve rounded area intervals and prevent gross/net or unknown-basis comparisons. |
| [Attachment Portability Audit](attachment-portability-audit) | Inspect ZIP paths without extraction: traversal, case/Unicode collisions, symlinks and Windows names. |
| [Brochure Table Recovery](brochure-table-recovery) | Review digital-PDF ruled tables, source boxes, manual edits and safe CSV/provenance exports. |

## Source-backed research

| Project | Original source and boundary |
| --- | --- |
| [Urbanisation Context Atlas](urbanisation-context-atlas) | World Bank/UN national urbanisation definitions; country context, not neighbourhood demand. |
| [Currency Context Atlas](currency-context-atlas) | Official annual IMF/WDI exchange rates, original observations and explicit2019-base arithmetic. |
| [Road Distance Reality Check](road-distance-reality-check) | Twelve reproducible OSRM route queries with endpoint snapping; not representative accessibility rankings. |
| [Tourism Recovery Gap Lab](tourism-recovery-gap-lab) | Annual UN Tourism/WDI arrivals, preserved missing years and a common baseline; no monthly-seasonality inference. |

Source snapshots, definitions and validation scripts accompany the analyses. Synthetic adversarial cases are used only for software tests and are labelled accordingly. No project establishes current property availability, authenticates documents, replaces a survey/legal review or forecasts investment performance.

## Reproduction

The verification workflow runs independent ecosystems in parallel on hosted runners. See each directory for local instructions. Python path/graph checks and research validators use the standard library; the PDF app and HTML parser declare their dependencies. .NET checks require SDK8+; PureScript uses the current pinned compiler/tool versions in CI.

Code and original analysis: MIT. Third-party observations, map data and dependencies retain their original source terms and attribution. Each publisher link is attribution, not a claim that NovAsia originated World Bank, IMF, UN or OpenStreetMap observations.
