# be-intl.com サイトリニューアル（静的 HTML / Git）

## 本番用ファイルはどこか

- **本番＝リポジトリのルート直下**の `index.html`・各 `*.html`・`assets/`・必要なルートの画像等です。URL は `https://be-intl.com/...` 既存のまま合わせています。
- **そのままサーバの公開ディレクトリに載せるのは、上記の集合だけ**にすると整理しやすいです。
- 詳細な「載せる／載せない」の一覧: **[docs/DEPLOY-FTP.ja.md](docs/DEPLOY-FTP.ja.md)**  
- 掲載候補ファイルのリスト出力: ルートで `.\tools\list-deploy-files.ps1` → `tools/last-deploy-list.txt`

## リポジトリ専用（本番不要）

- `docs/` … リデザイン仕様・旧サイト保管（`oldHP`）等  
- `tools/` … 体験談索引の `rebuild_taiken_index.py` 等  
- `.cursor/` … Cursor 用ルール  

## 体験談索引

- `taiken.html` の再生成: `python tools/rebuild_taiken_index.py`（`docs/oldHP/taiken-legacy-root-backup.html` を元データに使用）
