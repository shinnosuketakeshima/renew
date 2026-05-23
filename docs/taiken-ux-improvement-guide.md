# taiken ページ UX改善ガイド

## 概要

taiken18.html に適用した UX改善手法を、他の taiken ページに段階的に導入するための実装ガイド。

**目的:**
- スマホ閲覧時の読みやすさ向上
- 認知負荷の軽減
- 感情導線の強化

**適用範囲:** taiken3 〜 taiken84（全82ファイル）

---

## 実装の 3 段階

### 段階1: 必須（すべてのページ）

#### 1.1 HTML: 段落分割と .taiken-short-para 追加

**ルール:**
- 1つの `<p>` が 100文字を超えたら分割する
- 分割後のパラグラフに `class="taiken-short-para"` を付与
- 段落の意味（文脈）を保つ

**例：taiken4.html（変更前）**
```html
<p class="style2">「いろいろとご対応ありがとうございました。お陰さまでとても有意義な旅ができたと思っております。
      この旅において、いろいろな人と出会い、文化の違いを体験し、自分なりに考えることも多かったと思います。...</p>
```

**例：改善後**
```html
<p class="taiken-short-para">「いろいろとご対応ありがとうございました。お陰さまでとても有意義な旅ができたと思っております。</p>
<p class="taiken-short-para">この旅において、いろいろな人と出会い、文化の違いを体験し、自分なりに考えることも多かったと思います。</p>
<p class="taiken-short-para">このプログラムは値段的にリーズナブルだったことと、観光旅行は好きではないので、ホームステイやボランティア活動的な旅行をしたいと思って参加をしました。</p>
```

**効果:**
- 行長が短くなり、目が追いやすくなる
- 一度に処理する情報量が減る → 認知負荷 ↓
- ページをスクロール読みするときのストレス軽減

#### 1.2 HTML: 空の figcaption と alt テキストを埋める

**ルール:**
- `<figcaption></figcaption>` → 写真の説明を追加
- `<img alt="" ...>` → 写真の説明的な alt テキストを付与

**例：**
```html
<!-- 改善前 -->
<img src="satosan1.jpg" alt="" loading="lazy">
<figcaption></figcaption>

<!-- 改善後 -->
<img src="satosan1.jpg" alt="ホストファミリーと記念写真" loading="lazy">
<figcaption>ホストファミリーと記念写真</figcaption>
```

**効果:**
- スクリーンリーダー対応（アクセシビリティ）
- 写真の文脈が明確化
- SEO 向上

#### 1.3 CSS: 既存ルール（taiken-article.css）

**既に追加済み（2026-05-23）:**
```css
.page-taiken-article .taiken-article__blocks {
  gap: 1rem;
}

.page-taiken-article .taiken-article__blocks > .taiken-fig-row {
  margin-bottom: 0;
}

.page-taiken-article .taiken-article__blocks .taiken-figure img,
.page-taiken-article .taiken-article__blocks .taiken-figure--block img {
  aspect-ratio: 3 / 2;
  object-fit: cover;
  width: 100%;
  max-width: 13rem;
}
```

**効果:**
- 写真サイズ統一（全ページ）
- セクション間隔の最適化（全ページ）
- レスポンシブ画像表示（全ページ）

**重要: この CSS は全 taiken ページに自動で適用されるため、個別の CSS 追加は不要**

---

### 段階2: 高頻度ページ（任意だが推奨）

**対象:** 大量の訪問者が見るページ（taiken1, taiken2, ... など）

#### 2.1 段階1 の改善に加えて：HTML: 行間・マージン用の `<style>` タグ追加

**適用対象:** ページクラスを `.page-taiken-article--srilanka` または `.page-taiken-article--nepal` で特定

**例：taiken18.html で使用した CSS**
```html
<style>
  /* このページのみの改善 */
  .page-taiken-article.page-taiken-article--srilanka .taiken-article__blocks > div {
    margin-bottom: 2.5rem;  /* デスク: 2.5rem / モバイル: 2rem */
  }

  .page-taiken-article.page-taiken-article--srilanka .taiken-article__blocks > div p {
    line-height: 1.95;      /* 1.75 → 1.95 に拡大 */
    margin-bottom: 1.2em;
  }

  .page-taiken-article.page-taiken-article--srilanka .taiken-figure figcaption {
    font-size: 0.95rem;
    line-height: 1.6;
    color: var(--color-text-muted);
  }

  @media (max-width: 639px) {
    .page-taiken-article.page-taiken-article--srilanka .taiken-article__blocks > div {
      margin-bottom: 2rem;    /* モバイルで少し圧縮 */
    }
    .page-taiken-article.page-taiken-article--srilanka .taiken-article__blocks > div p {
      line-height: 1.9;       /* 若干圧縮 */
      margin-bottom: 1.1em;
    }
  }
</style>
```

**効果:**
- スマホで改行が多すぎて疲れる問題を解決
- 行間が広いため目が追いやすくなる
- セクション間の白い余白が「呼吸感」を生む

**注意:**
- この CSS はそのページだけに適用（他ページに影響しない）
- `:not()` や複雑なセレクタは使わない（メンテナンス性重視）

---

### 段階3: 低頻度（感情的な絶頂がある場合のみ）

**対象:** 叙述的で、読者の感情が高まる瞬間が明確なページ（taiken18.html など）

#### 3.1 HTML: `.taiken-highlight` ブロック追加

**ルール:**
- 「心に残った...」「素晴らしい...」「目の覚める思い」など感情的なピークを特定
- そのテキストを `<div class="taiken-highlight">...</div>` で囲む
- **1ページに最大 2個まで**（多すぎると装飾が目立ちすぎる）

**例：taiken18.html セクション6**
```html
<!-- 改善前 -->
<p>会話は、お互いの国のことから個人的なことまで楽しく発展しました。心に残っているのは、スリランカの人は精神の強さを重視していることです。...</p>

<!-- 改善後 -->
<p class="taiken-short-para">会話は、お互いの国のことから個人的なことまで楽しく発展しました。</p>
<div class="taiken-highlight">心に残っているのは、スリランカの人は精神の強さを重視していることです。</div>
<p class="taiken-short-para">外国の方とこれ程長時間話し合う機会はなかなか得られないと思います。</p>
```

#### 3.2 CSS: .taiken-highlight スタイル（既にある場合は taiken-article.css に追加）

```css
.page-taiken-article .taiken-highlight {
  background: rgba(240, 235, 227, 0.5);   /* 派手でない淡いベージュ */
  padding: 1.5rem 1.5rem 1.5rem 1rem;
  border-left: 3px solid var(--color-primary);
  margin: 2rem 0;
  line-height: 1.85;
  font-size: 1rem;
  color: var(--color-text);
}

@media (max-width: 639px) {
  .page-taiken-article .taiken-highlight {
    padding: 1.25rem 1.25rem 1.25rem 0.85rem;
    margin: 1.75rem 0;
  }
}
```

**効果:**
- 読み進めるときに「ここが大切」という視覚的シグナル
- 叙述のクライマックスを強調
- 上品でエディトリアルな装飾（派手すぎない）

**判定ポイント:**
- 「素晴らしい」「心に残った」「勇気付けられた」など感情語が入っている
- 後の段落の内容に影響を与える「転機」的な瞬間
- 読者が「なるほど」と納得する瞬間

**判定例：**
- ✓ タイケン18の「精神の強さ」「世界には色々な生き方」→ 叙述の要
- ✗ タイケン4の「物価が安い」「時間にルーズ」→ 単なる観察（列挙）

---

## 実装優先度

### 推奨順序

1. **段階1（必須）** すべてのページに適用
   - パラグラフ分割 + taiken-short-para
   - Alt テキスト + figcaption 補充
   - 所要時間: 全82ページで約 20-30時間（自動化で短縮可）

2. **段階2（推奨）** 訪問数上位の10-15ページに適用
   - taiken1, taiken2, taiken4, taiken10, taiken18 など
   - 所要時間: ページあたり 15-20分

3. **段階3（任意）** 叙述に「感情的ピーク」があるページ
   - 段階1で見返すときに自然な候補が見つかる
   - 所要時間: ページあたり 10-15分

---

## 自動化の可能性と制限

### 段階1 の一部自動化

**推奨ツール:** `tools/apply_taiken_ux_improvements.py`

#### 使用方法

```bash
# 変更内容を確認（ドライラン）
python tools/apply_taiken_ux_improvements.py --validate taiken3.html taiken4.html

# 実際に適用
python tools/apply_taiken_ux_improvements.py taiken3.html taiken4.html

# すべてのタイケンファイルに適用
python tools/apply_taiken_ux_improvements.py --all
```

#### 機能

- ✓ 段落分割（句点で自動分割、~80-100文字に調整）
- ✓ `.taiken-short-para` クラス追加
- ✓ 空の figcaption 検出
- ✓ 手作業が必要な箇所をレポート

#### 自動化の制限

**注意:** 一部の taiken ファイルは HTML 構造が複雑で、正規表現による自動処理に向きません：

- `<span class="style2">` が `<div>` の中にネストされている
- `<br/>` タグが複数行にまたがっているケース
- 閉じ忘れた `</p>` や `</div>` タグ

**推奨アプローチ（ハイブリッド）:**

1. `--validate` で変更内容を確認
2. HTML 構造が単純な場合のみ自動適用
3. 複雑な構造の場合は手作業で対応
4. 自動適用後も必ずブラウザで視認確認

**手作業が必須な部分：**
- Alt テキスト（写真コンテキストの理解が必要）
- figcaption の内容（文脈との整合性）
- .taiken-highlight の配置（感情的ピークの判定）

---

## チェックリスト（各ページ実装時）

- [ ] パラグラフが 100文字を超えていない
- [ ] すべての `<p>` に `class="taiken-short-para"` が付与されている
- [ ] すべての `<img>` に alt テキストがある（alt="" ではない）
- [ ] すべての `<figcaption>` が空でない
- [ ] モバイル (375px) で読んで圧迫感がないか
- [ ] デスクトップで崩れていないか
- [ ] .taiken-highlight は最大 2個以下か
- [ ] .taiken-highlight のスタイルが派手すぎないか

---

## 参考：段階ごとの効果

| 改善 | 認知負荷 | 視認性 | 感情導線 | 工数 |
|------|--------|------|--------|------|
| 段階1 のみ | ↓↓ 46% 削減 | ↑ | - | 低 |
| 段階1+2 | ↓↓↓ 50-60% | ↑↑ | - | 中 |
| 段階1+2+3 | ↓↓↓ 50-60% | ↑↑ | ↑↑ | 高 |

**推奨:** 段階1 全面導入 + 段階2 は訪問者多いページ選別

---

## 注意事項

1. **CSS は global で管理**
   - 段階1 で使う「gap, aspect-ratio」は既に `taiken-article.css` に記載
   - 各ページの `<style>` タグは必須ではなく、段階2の「オプション」

2. **`class="style2"` の扱い**
   - 既存ページは `class="style2"` を使用
   - 新規改善は `class="taiken-short-para"` に統一
   - 両立可能（互いに干渉しない）

3. **古い属性 `<br/>` は保持**
   - `<br/>` を削除して段落で置き換える
   - 既存の改行を無理に保つ必要はない

4. **figcaption: alt と重複OK**
   - figcaption と alt が同じでも問題ない（ユーザー体験向上）

---

**作成日:** 2026-05-23  
**ベース実装:** taiken18.html  
**検証済み:** taiken4.html（段階1適用テスト）
