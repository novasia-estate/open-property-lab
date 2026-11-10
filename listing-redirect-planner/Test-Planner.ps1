$ErrorActionPreference='Stop'
Import-Module "$PSScriptRoot/ListingRedirectPlanner.psd1" -Force
$script:checks=0
function Assert($condition,$name){if(-not $condition){throw $name};$script:checks++}
function Row($a,$b){[pscustomobject]@{Source=$a;Target=$b;Status=308}}
$p=Get-RedirectPlan @( (Row 'https://example.org/old' 'https://example.org/new') )
Assert ($p.Status -eq 'no_map_flags') 'Clean map'
$s=ConvertTo-NginxRedirectSnippet $p
Assert ($s.Contains('$is_args$args')) 'Default query preservation in snippet'
Assert ($s.Contains('location = /old')) 'Exact match'
$p=Get-RedirectPlan @((Row 'https://x.test/a' 'https://x.test/b'),(Row 'https://x.test/b' 'https://x.test/a'))
Assert (@($p.Issues | Where-Object Code -eq 'cycle').Count -eq 2) 'Cycle from both roots'
$p=Get-RedirectPlan @((Row 'https://x.test/a' 'https://x.test/b'),(Row 'https://x.test/b' 'https://x.test/c')) -MaxChainLength 1
Assert ($p.Rows[0].TerminalTarget -ceq 'https://x.test/c') 'Terminal target'
Assert (@($p.Issues | Where-Object Code -eq 'long_chain').Count -eq 1) 'Chain bound'
$p=Get-RedirectPlan @((Row 'https://x.test/a?old=1' 'https://x.test/b'))
Assert (@($p.Issues | Where-Object Code -eq 'query_policy_needed').Count -eq 1) 'Query not silently removed'
try{ConvertTo-NginxRedirectSnippet $p;throw 'Should reject flagged export'}catch{Assert ($_.Exception.Message -match 'Resolve all map flags') 'Flagged export rejected'}
$p=Get-RedirectPlan @((Row 'https://x.test/a' 'https://x.test/c'),(Row 'https://x.test/b' 'https://x.test/c'))
Assert (@($p.Issues | Where-Object Code -eq 'many_to_one_review').Count -eq 1) 'Convergence review'
$p=Get-RedirectPlan @((Row 'https://x.test/A' 'https://x.test/c'),(Row 'https://x.test/a' 'https://x.test/d'))
Assert ($p.Rows.Count -eq 2) 'Path case preserved'
foreach($bad in @('https://user:password@x.test/a','https://x.test/a#fragment','javascript:alert(1)')) {
 try{Get-RedirectPlan @((Row $bad 'https://x.test/b'));throw 'Should reject URL'}catch{Assert ($_.Exception.Message -match 'Require an absolute') 'Unsafe URL rejected'}
}
Test-ModuleManifest "$PSScriptRoot/ListingRedirectPlanner.psd1" | Out-Null
"PASS $script:checks redirect planner checks"
