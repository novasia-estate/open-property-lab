@{
 RootModule='ListingRedirectPlanner.psm1'
 ModuleVersion='1.0.0'
 GUID='2d9c6891-c35b-4ab0-bce4-168ee15bb92e'
 Author='NovAsia Estate'
 CompanyName='NovAsia Estate'
 Copyright='2026 NovAsia Estate; MIT'
 Description='Offline redirect-map graph review: cycles, chains, query policy and collisions, with guarded Nginx snippets.'
 PowerShellVersion='7.2'
 FunctionsToExport=@('Get-RedirectPlan','ConvertTo-NginxRedirectSnippet')
 CmdletsToExport=@();VariablesToExport=@();AliasesToExport=@()
 PrivateData=@{PSData=@{Tags=@('Redirects','Migration','PropertyData','Offline');LicenseUri='https://opensource.org/license/mit';ProjectUri='https://novasia.estate/';ReleaseNotes='First release: exact URL graph review and review-only Nginx snippets; no network calls or server changes.'}}
}
