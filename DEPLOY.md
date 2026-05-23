# デプロイ対象ファイル一覧

## 概要
このドキュメントは、FTP で本番サーバーにアップロードするファイルとフォルダを明示しています。

---

## ✅ アップロード必須

### HTML ページ（ルート）
```
index.html
postmail.html
srilanka.html
nepal.html
about.html
faq.html
voices.html
volunteer.html
living-basics.html
process1.html       (/flow/ の代わり)
program.html        (料金・コース)
yakkan.html         (約款・フッター)
privacy.html        (プライバシーポリシー・フッター)
links.html          (リンク集・フッター)
others.html         (航空券・保険・フッター)
site-guide.html     (サイト案内・フッター)
postmail.html       (資料請求フォーム)

# 体験記事（個別ページ）
taiken1.html ~ taiken84.html
```

### 画像・メディア（ルート）
```
*.jpg, *.JPG, *.gif  （参加者レポート・ホームページ画像）
```

### CSS / JavaScript
```
assets/css/
  ├── home.css           (共通トークン・レイアウト)
  ├── typography.css     (フォント・タイプスケール)
  ├── postmail.css       (フォーム・確認画面)
  ├── nepal.css          (ネパールページ固有)
  ├── srilanka.css       (スリランカページ固有)
  ├── faq.css
  ├── voices.css
  └── ... 他ページ固有のCSS

assets/js/
  ├── site-header-nav.js (ハンバーガーメニュー)
  ├── back-to-top.js     (トップ戻るボタン)
  ├── faq-accordion.js   (FAQ折りたたみ)
  └── card-visited.js    (訪問済みカード)
```

### CGI / サーバーサイドシステム
```
postmail.cgi        (フォーム処理メインスクリプト)
init.cgi            (postmail 設定ファイル)
check.cgi           (インストール確認スクリプト)

lib/                (CGI 依存モジュール)
  ├── CGI/
  ├── Jcode/
  └── Unicode/

tmpl/               (postmail のテンプレート)
  ├── conf.html     (確認画面)
  ├── thanks.html   (完了画面)
  ├── error.html    (エラー画面)
  ├── mail.txt      (管理者宛メール)
  └── reply.txt     (自動返信メール)
```

### その他必須ファイル
```
robots.txt          (SEO・クローラ管理)
sitemap.xml         (サイトマップ)
```

---

## ❌ アップロード不要

### Git / バージョン管理
```
.git/               (ローカル Git リポジトリ)
.gitignore          (Git 設定)
```

### IDE / エディタ設定
```
.cursor/            (Cursor IDE 設定)
.vscode/            (VS Code 設定 - もしあれば)
.claude/            (Claude 設定)
```

### ドキュメント・参考資料
```
docs/               (旧サイト・仕様書・参考資料)
  ├── oldHP/
  ├── be-intl-site-redesign-spec.md
  └── DEPLOY-FTP.ja.md
README.md
CLAUDE.md
GEMINI.md
DEPLOY.md           (このファイル)
```

### 開発・テールツール
```
tools/              (保守用スクリプト)
  ├── test_postmail_live.py
  ├── rebuild_taiken_index.py
  ├── generate-sitemap.ps1
  ├── list-deploy-files.ps1
  ├── seo-audit.ps1
  └── ... その他スクリプト

scripts/            (その他スクリプト)
src/                (ソースコード)
test2/              (テストフォルダ)
```

### データ / ログ（自動生成）
```
data/               (postmail ログ・セッション・自動生成)
  ├── log.cgi       (ログ - サーバーで自動生成)
  └── ses.cgi       (セッション - サーバーで自動生成)
```

### 素材・参考画像
```
Adobe_stock/        (Adobe Stock 素材 - ライセンス管理用)
SriLankaPhotos/     (写真素材参考)
assets/images/adobe-stock-sources.txt
```

### FTP ログ（ノイズ）
```
WS_FTP.LOG          (FTP ツール自動生成ログ)
```

### その他テスト・一時ファイル
```
userinput.py        (開発用)
*.md                (ドキュメント)
script.js           (旧スクリプト)
style.css           (旧スタイル)
conf.html           (ルートの旧ファイル)
```

---

## デプロイ手順

### 1. ファイルリストの確認（自動生成）
```bash
.\tools\list-deploy-files.ps1
# → tools/last-deploy-list.txt に生成
```

### 2. SEO 監査（エラーがないか確認）
```bash
.\tools\seo-audit.ps1
# Exit code 0 なら OK
```

### 3. FTP でアップロード
- **ホスト**: サーバー FTP アドレス
- **ユーザー**: FTP ユーザー名
- **パスワード**: FTP パスワード
- **対象ディレクトリ**: `/` (ドキュメントルート)

### 4. アップロード対象
`last-deploy-list.txt` を参照して、**include** リストのみをアップロード

### 5. 動作確認
- ブラウザで各ページを確認
- フォーム送信テスト
- モバイル表示確認

---

## 重要な注意

### lib/ と tmpl/ について
- **lib/** と **tmpl/** は CGI システムの必須ディレクトリです
- 本番サーバーで CGI が正常に動作するためには両方必須です
- アップロード時に忘れずに含めてください

### data/ ディレクトリについて
- **アップロード不要** です
- サーバーが自動生成するログ・セッションファイルを置く場所です
- サーバー側で以下の権限を設定してください：
  - パーミッション: `755` (CGI スクリプトから書き込み可能)

### Shift-JIS エンコーディング
- CGI スクリプト（`postmail.cgi`, `init.cgi`）は Shift-JIS エンコーディングです
- FTP アップロード時に **バイナリモード** を使用してください
- テキストモードでアップロードするとエンコーディングが崩れます

---

## トラブルシューティング

### フォーム送信時に「前画面に戻ってください」エラー
1. `init.cgi` の `$cf{back}` が `./index.html` になっているか確認
2. `lib/` と `tmpl/` がアップロードされているか確認
3. `data/` ディレクトリのパーミッション（755）を確認

### ページが表示されない
1. HTML ファイルが正しくアップロードされているか確認
2. CSS / JS が `assets/` ディレクトリに正しい構造で配置されているか確認

---

## 参考資料

- [`docs/DEPLOY-FTP.ja.md`](docs/DEPLOY-FTP.ja.md) - FTP デプロイの詳細手順
- [`docs/be-intl-site-redesign-spec.md`](docs/be-intl-site-redesign-spec.md) - サイト仕様書
