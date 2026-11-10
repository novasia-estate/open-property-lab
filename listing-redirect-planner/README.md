# Listing Redirect Planner

Review a catalogue URL migration as a graph before touching a web server. Read an explicit CSV of `Source,Target,Status`; identify cycles, self-redirects, long chains, duplicate sources, many-to-one consolidations and query policies requiring a human decision.

```powershell
Import-Module ./ListingRedirectPlanner.psd1
$plan = Get-RedirectPlan (Import-Csv ./examples/redirects.csv)
$plan | ConvertTo-Json -Depth 8 | Set-Content review.json -Encoding utf8
ConvertTo-NginxRedirectSnippet $plan # review-only output; never installed
```

PowerShell7.2+, no third-party dependencies. Source paths are case-sensitive; host normalization uses .NET URI parsing. Supported statuses:301,302,307,308. Snippets require an issue-free map and safe syntax. Queries in source URLs require manual rules because Nginx `location` matches paths. Ordinary source query parameters are preserved by the generated snippet unless the target explicitly supplies a query. Install each rule only in the appropriate source host's server block and verify the real server behavior yourself.

No URL is fetched. A flag-free map proves neither a live target nor indexing, canonical correctness or preserved business meaning. Many-to-one mappings may be intentional; review them instead of automatically rejecting a valid consolidation. No configuration is written or deployed by this module.

Run `pwsh -NoProfile -File Test-Planner.ps1`. Maintained by [NovAsia Estate](https://novasia.estate/); [source and issues](https://github.com/novasia-estate/open-property-lab/tree/main/listing-redirect-planner). MIT. Example domains are reserved documentation domains.
