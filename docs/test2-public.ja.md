# be-intl.com/test2/（本番用トップの表示確認用）

運用メモはリポジトリの `docs/test2-public.ja.md` に集約しています。FTP には `test2/index.html` と `test2/test2.css` のみをアップロードすれば足ります（本ドキュメントは不要）。

## 方針（実装の前提）

- `test2/index.html` は **本番「トップ」と同型の掲出**用です。検索にテスト版を出したくないため **`noindex, follow`** としています。
- **canonical** は `https://be-intl.com/test2/`（このディレクトリの正）です。

## 本番トップに差し替えるとき

1. `meta name="robots"` を `index,follow` にする（またはトップ本番の方針に合わせる）。
2. `link rel="canonical"` を `https://be-intl.com/` に差し替える。
3. **相対パス** `../` をルート用に書き直す（`../assets/` → `assets/` 等）。

## 配信

- 保存形式: **UTF-8（BOM なし）**。
- 推奨 HTTP ヘッダ: `Content-Type: text/html; charset=utf-8`。

## 参照パス

- `assets`・各 `.html` は親ディレクトリ向けの **`../`**。`/test2/` 配下で誤った相対解決を防ぎます。

## 共有スクリプト

- `assets/js/site-header-nav.js` … トップ `index.html` と共通（メニュー・Escape）。
