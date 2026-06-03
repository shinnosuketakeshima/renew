# デプロイの見分け方（短縮版）

**FTP で載せるファイル一覧**

```powershell
.\tools\list-deploy-files.ps1
# → tools/last-deploy-list.txt を参照してアップロード
```

| 載せる | 載せない |
|--------|----------|
| ルート `*.html`, 画像, `mail.php`, `robots.txt`, `sitemap.xml` | `docs/`, `tools/`, `scripts/`, `test2/` |
| `assets/` フォルダ全体 | `Nepal_photos/`, `SriLankaPhotos/` |
| | `*.md`, `FILE-GUIDE.txt`, `.git/`, `.cursor/` |

**詳細:** [docs/DEPLOY-FILES.ja.md](docs/DEPLOY-FILES.ja.md)  
**ルートの早見表:** [FILE-GUIDE.txt](FILE-GUIDE.txt)

公開前: `.\tools\seo-audit.ps1`（エラー 0）

---

旧 postmail CGI 方式の記述は [docs/DEPLOY-FILES.ja.md](docs/DEPLOY-FILES.ja.md) を参照（現在は `mail.php`）。
