# tools / 倉庫専用（FTP に上げない）

| ファイル | 説明 |
|----------|------|
| `rebuild_taiken_index.py` | 体験談索引 `../taiken.html` を再生成。元: `../docs/oldHP/taiken-legacy-root-backup.html` |
| `migrate_taiken_batch1.py` | 体験談HTMLの一括作業用（必要時のみ） |
| `list-deploy-files.ps1` | 本番候補ファイル一覧を `last-deploy-list.txt` に出力（PowerShell） |
| `_taiken_index.tsv` | 再生成の副産物（.gitignore 推奨） |

実行例（リポジトリルート）:

```bash
python tools/rebuild_taiken_index.py
```

```powershell
.\tools\list-deploy-files.ps1
```
