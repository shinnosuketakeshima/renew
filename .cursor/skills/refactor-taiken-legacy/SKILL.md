---
name: refactor-taiken-legacy
description: Refactor taiken*.html legacy article pages from table/font-based layout to responsive modern markup. Use when the user asks to clean spacer.gif, remove inline legacy attributes, replace table-based image/text rows with Flexbox, and keep article content intact.
---

# Refactor Taiken Legacy HTML

`taiken*.html` の旧式本文を、内容を保ったままレスポンシブ化するための手順。

## Scope

- 対象: `taiken*.html`
- 非対象: ヘッダー/ナビ/CTA の文言変更、本文の意味変更、URL変更

## Workflow

以下を順番に実施する。

1. 対象ファイルを読み、本文の旧式要素を特定する  
   - `spacer.gif`
   - `<table>` レイアウト
   - `<font ...>`
   - `&nbsp;` だけの要素
   - レイアウト専用属性（`width` `height` `border` `cellpadding` `cellspacing`）

2. `head` に最小スタイルを追加する  
   - `.container { margin: 0 auto; max-width: 1000px; width: 95%; }`
   - `.content-area { padding: 20px; line-height: 1.6; }`
   - `body` 背景は HTML 属性ではなく CSS (`background-image`) で制御

3. 本文を構造化し直す  
   - テーブルを `div/section/figure/p` に置換
   - 画像+テキスト横並びは `display:flex` ブロック化（例: `.story-block`）
   - 画像は `max-width:100%; height:auto;`
   - モバイルは 1 カラムに崩す

4. フッターの入れ子テーブルを簡素化  
   - 必要なら `<footer>` に一本化
   - 中央寄せは CSS で指定

5. `font` 指定を CSS 化  
   - 本文の文字サイズは `.content-area p { font-size: 1rem; }` を基準

## Guardrails

- 本文内容は勝手に要約しない
- 画像ファイル名とリンク先は維持
- `meta viewport` の `width=device-width` は削除しない
- 既存の共通クラス（`site-header` など）は壊さない

## Validation

編集後に次を確認する。

- `rg` で `spacer.gif|<font|&nbsp;|<table|cellpadding|cellspacing` が残っていない
- `ReadLints` で新規エラーがない
- 画像がスマホ幅ではみ出ない

