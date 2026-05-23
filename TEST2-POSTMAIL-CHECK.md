# test2/postmail.html チェック結果

## 🔍 チェック内容

### ✅ ページは表示されている
- https://be-intl.com/test2/postmail.html にアクセス可能
- HTML が正常にレンダリング
- フォーム要素も表示されている

### ❌ CGI が実行されていない（500 エラー）
- https://be-intl.com/test2/postmail/check.cgi → 500 エラー
- ロリポップのエラーメッセージ：「CGI が正しく動作していません」

---

## 🔧 原因と対策

### 原因1️⃣: CGI ディレクトリ制限
ロリポップでは CGI 実行ディレクトリが制限されている可能性：
- デフォルトでは `cgi-bin/` ディレクトリのみ
- ルート直下や `test2/postmail/` では実行不可

**対策**:
```
/cgi-bin/postmail/ ← ここに postmail/ を配置
```

### 原因2️⃣: パーミッション設定
CGI ファイルの実行権限が設定されていない

**対策**:
```bash
chmod 755 postmail.cgi init.cgi check.cgi
```

### 原因3️⃣: Perl パスが間違っている
ロリポップの Perl が別パスにある可能性

**確認方法**:
SSH で以下を実行：
```bash
which perl
```

`postmail.cgi` の最初の行を修正（例）：
```perl
#!/usr/bin/perl5        # ロリポップ標準の場合
```

---

## 📋 確認チェック

### ❌ ロリポップでの CGI 実行制限
1. FTP でサーバーに接続
2. `test2/postmail/postmail.cgi` を右クリック
3. **ファイルのプロパティ** → パーミッション確認
4. **755** に設定されているか？

### ❌ CGI ディレクトリ確認
ロリポップのコントロールパネルで以下を確認：
- CGI 実行可能ディレクトリの設定
- `test2/` で CGI 実行可能か？
- `cgi-bin/` に移動する必要はないか？

### ❌ Perl パス確認
SSH アクセスで：
```bash
which perl
perl -v | head -3
```

---

## 🛠️ 対策案

### 案1️⃣: ロリポップの cgi-bin ディレクトリを使用（推奨）
```
/cgi-bin/
├── postmail/
│   ├── postmail.cgi
│   ├── init.cgi
│   ├── check.cgi
│   ├── lib/
│   ├── tmpl/
│   └── data/
```

**postmail.html での form action:**
```html
<form action="/cgi-bin/postmail/postmail.cgi" method="post">
```

### 案2️⃣: ロリポップのサポートに問い合わせ
以下内容で問い合わせ：
```
件名: Perl CGI をルート直下で実行したい

本文:
・ロリポップを利用しています
・Perl CGI スクリプトをアップロード
・実行場所: test2/postmail/ ディレクトリ
・エラー: 500 Internal Server Error

・質問:
1. ルート直下で CGI 実行可能ですか？
2. CGI 実行可能なディレクトリは？
3. Perl のパスはどこですか？
```

---

## 次のステップ

1. **ロリポップのコントロールパネルで CGI 設定を確認**
2. **`cgi-bin/` 使用が必要な場合は、パスを修正**
3. **postmail.html の form action を修正**
4. **再度テスト**

---

## ロリポップでの CGI 標準パス

通常、ロリポップでは以下のパスが CGI 実行可能：
```
/cgi-bin/
/www/cgi-bin/
/usr/home/ユーザー名/cgi-bin/
```

本番環境に合わせた path を確認してください。
