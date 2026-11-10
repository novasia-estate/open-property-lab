Set-StrictMode -Version Latest

function ConvertTo-RedirectUri {
    param([Parameter(Mandatory)][string]$Value)
    $uri=$null
    if (-not [Uri]::TryCreate($Value,[UriKind]::Absolute,[ref]$uri) -or $uri.Scheme -notin @('https','http') -or $uri.UserInfo -or $uri.Fragment -or $Value -match '[\r\n\\]') { throw "Require an absolute HTTP(S) URL without credentials, fragment or backslash: $Value" }
    $uri
}

function Get-RedirectPlan {
    <# .SYNOPSIS Inspect an explicit redirect map without contacting URLs or changing any server. #>
    [CmdletBinding()]
    param([Parameter(Mandatory)][object[]]$Rows,[ValidateRange(1,100)][int]$MaxChainLength=3)
    $issues=[Collections.Generic.List[object]]::new();$entries=[Collections.Generic.List[object]]::new()
    $map=[Collections.Generic.Dictionary[string,object]]::new([StringComparer]::Ordinal)
    foreach($row in $Rows) {
        if (-not $row.PSObject.Properties['Source'] -or -not $row.PSObject.Properties['Target']) { throw 'Every row must contain Source and Target.' }
        $from=ConvertTo-RedirectUri ([string]$row.Source);$to=ConvertTo-RedirectUri ([string]$row.Target)
        $status=301
        if($row.PSObject.Properties['Status'] -and [string]$row.Status) {
            if(-not [int]::TryParse([string]$row.Status,[ref]$status) -or $status -notin @(301,302,307,308)) { throw 'Status must be301,302,307 or308.' }
        }
        $entry=[pscustomobject]@{Source=$from.AbsoluteUri;Target=$to.AbsoluteUri;Status=$status;ChainLength=0;TerminalTarget=$to.AbsoluteUri;SourceQuery=$from.Query;TargetQuery=$to.Query}
        if($map.ContainsKey($entry.Source)) { $issues.Add([pscustomobject]@{Code='duplicate_source';Source=$entry.Source;Detail='Multiple rows for one exact source; resolve before export.'});continue }
        if($entry.Source -ceq $entry.Target) {$issues.Add([pscustomobject]@{Code='self_redirect';Source=$entry.Source;Detail='Source equals target.'})}
        if($from.Query) {$issues.Add([pscustomobject]@{Code='source_query_requires_manual_rule';Source=$entry.Source;Detail='Nginx location matches paths, not queries. Review this row manually.'})}
        if($from.Query -and -not $to.Query) {$issues.Add([pscustomobject]@{Code='query_policy_needed';Source=$entry.Source;Detail='Target omits source query. Decide preservation, transformation or removal.'})}
        $map.Add($entry.Source,$entry);$entries.Add($entry)
    }
    foreach($entry in $entries) {
        $seen=[Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal);$current=$entry.Source;$length=0
        while($map.ContainsKey($current)) {
            if(-not $seen.Add($current)) {$issues.Add([pscustomobject]@{Code='cycle';Source=$entry.Source;Detail="Cycle reaches $current"});break}
            $length++;$current=$map[$current].Target
        }
        $entry.ChainLength=$length;$entry.TerminalTarget=$current
        if($length -gt $MaxChainLength){$issues.Add([pscustomobject]@{Code='long_chain';Source=$entry.Source;Detail="Chain length $length exceeds $MaxChainLength"})}
    }
    foreach($group in @($entries | Group-Object Target | Where-Object Count -gt 1)) {
        $issues.Add([pscustomobject]@{Code='many_to_one_review';Source=(@($group.Group.Source)-join ', ');Detail="Multiple sources converge on $($group.Name); consolidation may be intentional."})
    }
    [pscustomobject]@{SchemaVersion=1;Rows=@($entries.ToArray());Issues=@($issues.ToArray());NetworkChecked=$false;Status=if($issues.Count){'review_required'}else{'no_map_flags'}}
}

function ConvertTo-NginxRedirectSnippet {
    <# .SYNOPSIS Produce review-only snippets for exact path maps; never installs server configuration. #>
    [CmdletBinding()]
    param([Parameter(Mandatory)]$Plan)
    if(@($Plan.Issues).Count){throw 'Resolve all map flags before generating configuration.'}
    $lines=[Collections.Generic.List[string]]::new();$lines.Add('# Review before use. Place each rule in the server block for its source host.')
    foreach($row in $Plan.Rows) {
        $from=ConvertTo-RedirectUri $row.Source;$to=ConvertTo-RedirectUri $row.Target
        if($from.AbsoluteUri -match '[;{}$"\s]' -or $to.AbsoluteUri -match '[;{}$"\s]'){throw 'URL contains unsupported configuration characters; manual rule required.'}
        $suffix=if($to.Query){''}else{'$is_args$args'}
        $lines.Add("# Source host: $($from.Authority)")
        $lines.Add(('location = '+$from.AbsolutePath+' { return '+$row.Status+' '+$to.AbsoluteUri+$suffix+'; }'))
    }
    $lines -join "`n"
}
Export-ModuleMember -Function Get-RedirectPlan,ConvertTo-NginxRedirectSnippet
