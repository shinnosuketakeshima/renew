<#
.SYNOPSIS
  Audits root-level *.html for internal SEO checklist (canonical, title, description, H1 count, img alt).

.DESCRIPTION
  Reads d:\github\renew\*.html (adjust $Root if needed). Exit code 1 if any ERROR line is printed.
  Does not modify files.
  FAQPage JSON-LD vs visible Q/A must be verified separately when FAQ body changes (not automated here).

.EXAMPLE
  pwsh -File tools/seo-audit.ps1
#>
$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path

$files = Get-ChildItem -Path $RepoRoot -Filter '*.html' -File | Sort-Object Name
$exit = 0
foreach ($f in $files) {
  $raw = [System.IO.File]::ReadAllText($f.FullName, [System.Text.UTF8Encoding]::new($false))
  $name = $f.Name
  $issues = @()

  if ($raw -notmatch 'rel\s*=\s*["'']canonical["'']') { $issues += 'ERROR: missing link rel=canonical' }
  if ($raw -notmatch '<meta\s+charset\s*=\s*["'']utf-8["'']') { $issues += 'WARN: missing meta charset=utf-8' }
  if ($raw -notmatch 'name\s*=\s*["'']viewport["'']') { $issues += 'WARN: missing meta viewport' }
  if ($raw -notmatch '<title[^>]*>[^<]+</title>') { $issues += 'ERROR: missing or empty title' }
  if ($raw -notmatch 'name\s*=\s*["'']description["'']') { $issues += 'WARN: missing meta description' }

  $h1Count = ([regex]::Matches($raw, '<h1\b', 'IgnoreCase')).Count
  if ($h1Count -eq 0) { $issues += 'WARN: no h1' }
  if ($h1Count -gt 1) { $issues += "WARN: multiple h1 ($h1Count)" }

  $imgTags = [regex]::Matches($raw, '<img\b[^>]*>', 'IgnoreCase')
  foreach ($m in $imgTags) {
    $tag = $m.Value
    if ($tag -notmatch '\salt\s*=\s*') { $issues += "WARN: img missing alt: $($tag.Substring(0, [Math]::Min(80, $tag.Length)))..." }
  }

  if ($issues.Count -gt 0) {
    Write-Output "---- $name ----"
    foreach ($i in $issues) {
      Write-Output "  $i"
      if ($i -match '^ERROR') { $exit = 1 }
    }
  }
}

if ($exit -ne 0) {
  Write-Output "`nAudit finished with ERRORS."
} else {
  Write-Output "`nAudit finished (no ERROR-level issues; review WARN)."
}
exit $exit
