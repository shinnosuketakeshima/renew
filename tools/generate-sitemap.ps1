<#
.SYNOPSIS
  Writes sitemap.xml at repository root (delegates to tools/generate_sitemap.py).

.EXAMPLE
  pwsh -File tools/generate-sitemap.ps1
#>
$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Push-Location $RepoRoot
try {
  python tools/generate_sitemap.py
  if ($LASTEXITCODE -ne 0) { throw "generate_sitemap.py failed with exit $LASTEXITCODE" }
} finally {
  Pop-Location
}
