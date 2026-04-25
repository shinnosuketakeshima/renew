# 本番(FTP)に載せる候補のファイルを一覧（docs / tools / .git 等を除外）
# 使い方: リポジトリルートで  .\tools\list-deploy-files.ps1
# 出力:   tools/last-deploy-list.txt

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$OutFile  = Join-Path $PSScriptRoot 'last-deploy-list.txt'

# リポジトリ内で「公開ルートに含めない」パス（$RepoRoot からの相対にマッチ）
$excludeRelativePatterns = @(
  '^[\\/]\.git[\\/]'
  '^[\\/]docs[\\/]'
  '^[\\/]tools[\\/]'
  '^[\\/]\.cursor[\\/]'
  '^[\\/]\.github[\\/]'
  '^[\\/]node_modules[\\/]'
  '^[\\/]README\.md$'
  '^[\\/]\.gitignore$'
  '^[\\/]\.editorconfig$'
)

function Test-DeployPath {
  param([string]$rel)
  $norm = $rel -replace '\\', '/'
  foreach ($p in $excludeRelativePatterns) {
    if ($norm -match $p) { return $false }
  }
  return $true
}

$lines = [System.Collections.Generic.List[string]]::new()
Get-ChildItem -Path $RepoRoot -Recurse -File -Force | ForEach-Object {
  $rel = $_.FullName.Substring($RepoRoot.Length)
  if (Test-DeployPath -rel $rel) {
    $lines.Add($rel.TrimStart('\', '/'))
  }
}
$lines.Sort()
$utf8Bom = New-Object System.Text.UTF8Encoding $true
[System.IO.File]::WriteAllLines($OutFile, $lines, $utf8Bom)
Write-Host "Wrote $OutFile ($($lines.Count) files) relative to repo root."
