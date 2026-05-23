# デプロイ対象・除外判定リファレンス

このファイルは **ルートディレクトリのファイル・フォルダ** について、
FTP でのアップロード対象かどうかを一覧で示しています。

---

## ディレクトリ構造と判定

```
.cursor/                ❌ アップロード不要（IDE 設定）
.claude/                ❌ アップロード不要（IDE 設定）
.git/                   ❌ アップロード不要（Git リポジトリ）
.gitignore              ✅ ルートに含めない（Git 管理用）

Adobe_stock/            ❌ アップロード不要（素材・参考用）
SriLankaPhotos/         ❌ アップロード不要（素材・参考用）
assets/                 ✅ アップロード必須
  ├── css/              ✅ すべての CSS ファイル
  └── js/               ✅ すべての JavaScript ファイル

data/                   ❌ アップロード不要
  ├── log.cgi           ❌ 自動生成ログ
  ├── ses.cgi           ❌ セッション管理
  └── WS_FTP.LOG        ❌ FTP ログ

docs/                   ❌ アップロード不要（ドキュメント）
  ├── oldHP/            ❌ 旧サイト参考
  ├── be-intl-site-redesign-spec.md
  ├── EDIT-POINTS.txt
  └── DEPLOY-FTP.ja.md

postmail/               ✅ アップロード必須（CGI システム全体）
  ├── postmail.cgi      ✅ フォーム処理スクリプト
  ├── init.cgi          ✅ 設定ファイル
  ├── check.cgi         ✅ 診断スクリプト
  ├── lib/              ✅ CGI 依存モジュール
  │   ├── CGI/
  │   ├── Jcode/
  │   └── Unicode/
  ├── tmpl/             ✅ CGI テンプレート
  │   ├── conf.html     ✅ 確認画面
  │   ├── thanks.html   ✅ 完了画面
  │   ├── error.html    ✅ エラー画面
  │   ├── mail.txt      ✅ メールテンプレート
  │   └── reply.txt     ✅ 自動返信テンプレート
  └── data/             ✅ ログ・セッション（自動生成）
      ├── log.cgi
      └── ses.cgi

tools/                  ❌ アップロード不要（開発・メンテナンス用）
  ├── test_postmail_live.py
  ├── postmail-test-output.txt
  ├── live-postmail-form.html
  └── ... その他スクリプト
```

---

## ルートのファイル判定

```
.gitignore              ❌ アップロード不要
CLAUDE.md               ❌ アップロード不要
DEPLOY.md               ❌ アップロード不要（このファイル）
GEMINI.md               ❌ アップロード不要
README.md               ❌ アップロード不要

robots.txt              ✅ アップロード必須
sitemap.xml             ✅ アップロード必須

*.html                  ✅ アップロード必須
  ├── index.html
  ├── postmail.html
  ├── srilanka.html
  ├── nepal.html
  ├── about.html
  ├── faq.html
  ├── voices.html
  ├── volunteer.html
  ├── living-basics.html
  ├── process1.html
  ├── program.html
  ├── privacy.html
  ├── yakkan.html
  ├── links.html
  ├── others.html
  ├── site-guide.html
  └── taiken1.html ~ taiken84.html

*.jpg, *.JPG, *.gif    ✅ アップロード必須（画像）

*.cgi                  ✅ アップロード必須（CGI）
  ├── postmail.cgi
  ├── init.cgi
  └── check.cgi

*.py, *.js             ❌ アップロード不要（開発用）
  ├── userinput.py
  └── script.js (旧)

*.css, *.md (ルート)   ❌ アップロード不要
  ├── style.css (旧)
  └── *.md ドキュメント

old*.html              ❌ アップロード不要（旧ファイル）
conf.html (ルート)     ❌ アップロード不要（tmpl/ に移動）

WS_FTP.LOG             ❌ アップロード不要（FTP ログ）
```

---

## クイック判定

### これらはアップロードしてください ✅
- `assets/` ディレクトリ内の **すべてのファイル**
- `postmail/` ディレクトリ内の **すべてのファイル・フォルダ**
  - `postmail/postmail.cgi`, `postmail/init.cgi`, `postmail/check.cgi`
  - `postmail/lib/` （CGI 依存モジュール）
  - `postmail/tmpl/` （テンプレート）
  - `postmail/data/` （ログ・セッションディレクトリ）
- ルートの `*.html`（taiken1.html ~ taiken84.html を含む）
- ルートの `*.jpg`, `*.JPG`, `*.gif`（画像）
- `robots.txt`, `sitemap.xml`

### これらはアップロードしないでください ❌
- `.git/`, `.cursor/`, `.claude/` などのドットフォルダ
- `docs/`, `tools/`, `scripts/`, `src/`, `test2/`
- `Adobe_stock/`, `SriLankaPhotos/`
- `*.md`, `CLAUDE.md`, `DEPLOY.md` などのドキュメント
- `WS_FTP.LOG` や他の FTP ログ
- 旧ファイル（`style.css` ルート版など）

---

## デプロイ方法

### PowerShell スクリプトを使用（推奨）
```powershell
# 対象ファイルをリスト化
.\tools\list-deploy-files.ps1

# 出力ファイル
# → tools/last-deploy-list.txt
```

この出力ファイルを参照して、**include** リストのファイルのみ FTP でアップロードしてください。

### 手動アップロード
FTP クライアント（FileZilla など）で、以下のディレクトリ・ファイルのみをアップロード：

```
/
├── assets/              ← ディレクトリ全体
├── postmail/            ← ディレクトリ全体（CGI システム）
│   ├── postmail.cgi
│   ├── init.cgi
│   ├── check.cgi
│   ├── lib/
│   ├── tmpl/
│   └── data/
├── index.html
├── postmail.html
├── srilanka.html
├── nepal.html
├── ... (その他ページ HTML)
├── robots.txt
├── sitemap.xml
└── (すべての .jpg, .JPG, .gif)
```

---

## 重要な注意

### postmail/ ディレクトリ全体が必須
- **postmail/** ディレクトリ内のすべてのファイル・フォルダをアップロードしてください
- 以下を含む：
  - `postmail.cgi`, `init.cgi`, `check.cgi`
  - `lib/` - CGI 依存モジュール
  - `tmpl/` - テンプレート（HTML・メール）
  - `data/` - ログ・セッション用（自動生成）

### data/ ディレクトリについて
- ローカルからのアップロード不要です（`log.cgi`, `ses.cgi` は本番で自動生成）
- ただしディレクトリ自体は作成・維持してください
- パーミッション設定：**755** 以上の書き込み権限が必要

### ファイルアップロードモード
- CGI スクリプト（`*.cgi`）は **バイナリモード** でアップロード
- HTML は **テキストモード** でも大丈夫

---

## 参照
- [DEPLOY.md](DEPLOY.md) - 詳細ガイド
- [docs/DEPLOY-FTP.ja.md](docs/DEPLOY-FTP.ja.md) - FTP 手順書
