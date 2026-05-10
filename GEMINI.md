# GEMINI.md - Beインターナショナル サイトリニューアル

## プロジェクト概要
このプロジェクトは、スリランカとネパールへの語学留学（個人レッスン＋ホームステイ）を提供する**Beインターナショナル (be-intl.com)** の公式サイトの全面リニューアルプロジェクトです。2004年設立当時の古いテーブルレイアウトのサイトを、現代的でモバイルフレンドリーな「ブティック・トラベル・マガジン / エディトリアル」スタイルの静的サイトへと刷新しています。

### 主要技術・構成
- **技術スタック:** 純粋な静的HTML / CSS / JavaScript (Vanilla)
- **フレームワーク/ビルドツール:** なし（ビルド工程不要）
- **デプロイ:** FTPによる手動アップロード（リポジトリルートのファイルが本番環境）
- **デザイン:** CSSカスタムプロパティ（デザイントークン）を使用したモダンな設計

## 開発・運用ガイドライン
詳細な設計書は `docs/be-intl-site-redesign-spec.md` に記載されており、これが**絶対的な正解（Canonical Authority）**です。

### 基本ルールと制約
- **共通ヘッダー・フッター:** 全ページでHTMLを複製（サーバーサイドインクルードなし）。
- **フォームシステム:** 既存の `postmail` システムを維持。フィールドの増減や `tel:` リンクの追加は禁止。
- **SNS連携:** LINEやSNSのボタン配置、外部埋め込みは行わない。
- **UIトーン:** 「旅」よりも「誰かの日常にお邪魔する」感覚。清潔感のある、静かで贅沢な（Quiet Luxury）エディトリアルデザイン。
- **SEO:** 各ページに固有の `<title>`, `<meta name="description">`, `<link rel="canonical">` を設定し、JSON-LD（Organization, FAQPage等）を配置する。
- **カードデザインの統一:** サイト内のカード型要素（体験談、抜粋等）は、以下のスタイルで統一する。
    - **角丸:** 12px (`var(--radius-lg)` 相当)
    - **左の差し色:** 4px のボーダー (`border-left`)。色は主張しすぎないグレー（`#d1d5db` や `rgba(var(--color-primary-rgb), 0.2)`）を基本とする。
    - **ホバー時:** 5px 浮き上がり (`translateY(-5px)`) と影の強調。カード全体をクリック可能にする（Stretched Link）。

### 主要コマンド (PowerShell)
```powershell
# 体験談インデックス (taiken.html) の再生成
python tools/rebuild_taiken_index.py

# 本番デプロイ対象ファイルのリスト出力 (tools/last-deploy-list.txt)
.\tools\list-deploy-files.ps1
```

## アーキテクチャとディレクトリ構成

| ディレクトリ | 内容・役割 |
|---|---|
| `/` (Root) | **本番公開用HTMLページ** (`index.html`, `srilanka.html` 等) および画像。 |
| `assets/css/` | `home.css` (基本設計・トークン), `typography.css` (フォント), その他各ページ用CSS。 |
| `assets/js/` | `site-header-nav.js` (メニュー制御), `back-to-top.js` (トップに戻るボタン)。 |
| `docs/` | `be-intl-site-redesign-spec.md` (設計書), 旧サイトのバックアップ (`oldHP/`)。 |
| `tools/` | メンテナンス用スクリプト (Python/PowerShell)。 |

## デザインシステム (Design Tokens)
すべてのトークンは `assets/css/home.css` の `:root` で定義されています。

| 変数名 | 値 | 役割 |
|---|---|---|
| `--color-bg` | `#f7f5f0` | ウォームアイボリー（メイン背景） |
| `--color-text` | `#2a2724` | チャコール（本文） |
| `--color-primary` | `#1c1c28` | ディープネイビー（リンク・ボタン） |
| `--radius-md` | `2px` | ほぼ角ばった角丸（エディトリアル感） |
| `--font-sans` | `Inter`, `Noto Sans JP` | 標準フォント |

## 注意事項
- ネパールとスリランカは対等に扱う。ネパールを「格下」として扱わない。
- ターゲット層は30-40代の女性、一人旅を検討している層。
- 景品表示法に抵触する表現（「業界最安値」「No.1」など）は絶対に使用しない。
- ページ内の画像 `SriLankaPhotos/` などは既存資産を活用している。
