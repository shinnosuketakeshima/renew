# 本番(FTP)に載せる候補 / 載せないファイルを一覧化
# 使い方（リポジトリルート）:
#   .\tools\list-deploy-files.ps1
# 出力:
#   tools/last-deploy-list.txt      … FTP アップロード対象
#   tools/local-only-list.txt       … 作業用（アップロード不要）
#   tools/deploy-summary.txt        … 両方の件数とフォルダ別内訳

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$DeployList = Join-Path $PSScriptRoot 'last-deploy-list.txt'
$LocalList  = Join-Path $PSScriptRoot 'local-only-list.txt'
$Summary    = Join-Path $PSScriptRoot 'deploy-summary.txt'

# リポジトリ内で「公開ルートに含めない」パス（/ 区切り・先頭からマッチ）
$excludeRelativePatterns = @(
  '^\.git/'
  '^\.cursor/'
  '^\.claude/'
  '^\.github/'
  '^\.vscode/'
  '^docs/'
  '^tools/'
  '^scripts/'
  '^src/'
  '^test2/'
  '^Nepal_photos/'
  '^SriLankaPhotos/'
  '^node_modules/'
  '\.md$'
  '^\.gitignore$'
  '^\.editorconfig$'
  '^userinput\.py$'
  '^WS_FTP\.LOG$'
  '^FILE-GUIDE\.txt$'
  '^conf\.html$'                    # 旧 postmail 確認画面（ルート）
  '^script\.js$'                    # 旧サイト用
  '^script-back\.js$'
  '^style\.css$'                    # 旧サイト用
  '^assets/images/adobe-stock-sources\.txt$'
  '\.png$'                          # ルートの作業用キャプチャ等
  '^CGI-'
)

function Test-DeployPath {
  param([string]$rel)
  $norm = ($rel -replace '\\', '/').TrimStart('/')
  foreach ($p in $excludeRelativePatterns) {
    if ($norm -match $p) { return $false }
  }
  return $true
}

function Get-TopFolder {
  param([string]$rel)
  $norm = ($rel -replace '\\', '/').TrimStart('/')
  if ($norm -notmatch '/') { return '(ルートのファイル)' }
  return ($norm -split '/')[0]
}

$deploy = [System.Collections.Generic.List[string]]::new()
$local  = [System.Collections.Generic.List[string]]::new()

Get-ChildItem -Path $RepoRoot -Recurse -File -Force | ForEach-Object {
  $rel = $_.FullName.Substring($RepoRoot.Length).TrimStart('\', '/')
  if (Test-DeployPath -rel $rel) {
    $deploy.Add($rel)
  } else {
    $local.Add($rel)
  }
}

$deploy.Sort()
$local.Sort()

$utf8Bom = New-Object System.Text.UTF8Encoding $true
[System.IO.File]::WriteAllLines($DeployList, $deploy, $utf8Bom)
[System.IO.File]::WriteAllLines($LocalList, $local, $utf8Bom)

$summaryLines = [System.Collections.Generic.List[string]]::new()
$summaryLines.Add('be-intl.com デプロイ対象サマリー')
$summaryLines.Add("生成: $(Get-Date -Format 'yyyy-MM-dd HH:mm')")
$summaryLines.Add('')
$summaryLines.Add("FTP アップロード対象: $($deploy.Count) ファイル → tools/last-deploy-list.txt")
$summaryLines.Add("作業用（不要）      : $($local.Count) ファイル → tools/local-only-list.txt")
$summaryLines.Add('')
$summaryLines.Add('--- アップロード対象（フォルダ別 上位）---')
$deploy | ForEach-Object { Get-TopFolder $_ } | Group-Object | Sort-Object Count -Descending | Select-Object -First 12 | ForEach-Object {
  $summaryLines.Add(("  {0,-22} {1,4} 件" -f $_.Name, $_.Count))
}
$summaryLines.Add('')
$summaryLines.Add('--- アップロード不要（フォルダ別 上位）---')
$local | ForEach-Object { Get-TopFolder $_ } | Group-Object | Sort-Object Count -Descending | Select-Object -First 12 | ForEach-Object {
  $summaryLines.Add(("  {0,-22} {1,4} 件" -f $_.Name, $_.Count))
}
$summaryLines.Add('')
$summaryLines.Add('詳細: docs/DEPLOY-FILES.ja.md / ルート FILE-GUIDE.txt')

[System.IO.File]::WriteAllLines($Summary, $summaryLines, $utf8Bom)

Write-Host ""
Write-Host "=== be-intl.com デプロイファイル一覧 ===" -ForegroundColor Cyan
Write-Host "アップロード対象 : $($deploy.Count) 件 -> $DeployList"
Write-Host "作業用（不要）   : $($local.Count) 件 -> $LocalList"
Write-Host "サマリー         : $Summary"
Write-Host ""
Write-Host "FTP では last-deploy-list.txt のみアップロードしてください。" -ForegroundColor Yellow
