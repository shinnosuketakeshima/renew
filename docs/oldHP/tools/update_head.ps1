param(
    [string]$Root,
    [string]$Filter = '*.html',
    [switch]$Recurse,
    [string[]]$ExcludeNames = @()
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path $Root)) { throw "Root not found: $Root" }

$targetFiles = if ($Recurse) {
    Get-ChildItem -Path $Root -Filter $Filter -File -Recurse
} else {
    Get-ChildItem -Path $Root -Filter $Filter -File
}

if ($ExcludeNames.Count -gt 0) {
    $targetFiles = $targetFiles | Where-Object { $_.Name -notin $ExcludeNames }
}

Write-Host ("TARGETS=" + $targetFiles.Count)
if (-not $targetFiles) { exit 0 }

$timestamp = (Get-Date).ToString('yyyyMMdd_HHmmss')
$backupRoot = Join-Path $Root ("backup_compat_" + $timestamp)
New-Item -ItemType Directory -Path $backupRoot | Out-Null

# Regexes
$reDoctype = '(?is)^\s*<!DOCTYPE[^>]*>\s*'
$reViewport = '(?is)<meta[^>]+name\s*=\s*\"viewport\"[^>]*>\s*'
$reCharset = '(?is)<meta\s+charset\s*=\s*\"[^\"]*\"\s*/?>\s*'
$reHead = '(?is)<head[^>]*>'
$reHtml = '(?is)<html[^>]*>'
$reHttpEq = '(?is)<meta[^>]+http-equiv\s*=\s*\"content-type\"[^>]*>'
$reMetaAfterHead = '(?is)</head>\s*(?:<meta[^>]*>\s*)+'

$ok = 0
foreach ($f in $targetFiles) {
    try {
        $rel = $f.FullName.Substring($Root.Length).TrimStart('\\')
        $destPath = Join-Path $backupRoot $rel
        $destDir = Split-Path $destPath
        if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
        Copy-Item $f.FullName $destPath -Force

        $c = Get-Content -Raw -LiteralPath $f.FullName
        $c = [regex]::Replace($c, $reDoctype, '')
        $c = [regex]::Replace($c, $reViewport, '')
        $c = [regex]::Replace($c, $reCharset, '')
        if ($c -notmatch $reHead) { $c = [regex]::Replace($c, $reHtml, '<html>`r`n<head>`r`n</head>') }
        if ($c -match $reHead) {
            $c = [regex]::Replace($c, $reHttpEq, '')
            $insert = "`r`n    <meta http-equiv=`"content-type`" content=`"text/html; charset=utf-8`">"
            $c = [regex]::Replace($c, '(?is)(<head[^>]*>)', '$1' + $insert, 1)
        }
        $c = [regex]::Replace($c, $reMetaAfterHead, '</head>')
        $c = [regex]::Replace($c, '\r?\n{3,}', '`r`n`r`n')
        Set-Content -LiteralPath $f.FullName -Encoding UTF8 -NoNewline -Value $c
        $ok++
        Write-Host ("OK " + $rel)
    } catch {
        Write-Host ("ERR " + $f.FullName + ': ' + $_)
    }
}

Write-Host ("DONE=" + $ok)


