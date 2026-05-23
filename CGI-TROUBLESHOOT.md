# CGI 実行問題のトラブルシューティング

## 症状
postmail.html からフォーム送信 → CGI のテキストファイルが表示される

## 原因の可能性

### 1️⃣ **CGI 実行権限がない（最も可能性が高い）**
サーバー側で `.cgi` ファイルの実行権限（パーミッション）が設定されていない

```bash
# Linux/Unix サーバーで必要な設定
chmod 755 postmail.cgi
chmod 755 init.cgi
chmod 755 check.cgi
```

### 2️⃣ **CGI ディレクトリが指定されていない**
Web サーバー（Apache など）の設定で、CGI を実行できるディレクトリが限定されている場合がある
- 通常は `cgi-bin/` ディレクトリのみで実行可能
- ルート（`/`）で CGI 実行が有効になっていない

### 3️⃣ **Perl の場所が異なる**
シェバン行（ファイルの最初の行）で指定されている Perl パスが、サーバーに存在しない

```perl
#!/usr/local/bin/perl  ← この行が重要
```

サーバーの Perl が別の場所にある場合：
```bash
which perl  # Perl の場所を確認
```

### 4️⃣ **form action のパスが間違っている**
postmail.html の form action を確認

```html
<form ... action="./postmail.cgi" method="post">
```

- `./postmail.cgi` → ルートの postmail.cgi
- `cgi-bin/postmail.cgi` → cgi-bin フォルダ内（もしそこにアップロードした場合）

---

## 確認手順

### ステップ1: サーバーのファイル構造を確認
FTP クライアントで以下を確認：

```
/ (ドキュメントルート)
├── postmail.html      ← 確認
├── postmail.cgi       ← ここにあるはず
├── init.cgi
├── check.cgi
├── lib/
├── tmpl/
└── ...
```

✅ `postmail.cgi` がルートにあることを確認

### ステップ2: ファイルのパーミッション確認
FTP クライアント（FileZilla など）の「ファイルのプロパティ」で、以下を確認：

```
postmail.cgi: パーミッション 755 または 775
init.cgi:     パーミッション 755 または 775
check.cgi:    パーミッション 755 または 775
```

#### FileZilla での確認手順
1. `postmail.cgi` を右クリック
2. 「ファイルのプロパティ」を選択
3. 「パーミッション」を確認
4. 必要に応じて `755` に変更

### ステップ3: Perl パスの確認
SSH でサーバーにアクセスできる場合：

```bash
which perl
# または
perl -v | head -3
```

もし Perl のパスが異なる場合は、`postmail.cgi` と `init.cgi` の最初の行を修正：

```perl
#!/usr/bin/perl        # 修正例 1
#!/usr/bin/perl5       # 修正例 2
#!/usr/local/bin/perl  # 元の設定
```

### ステップ4: Web サーバー設定を確認
ホスティング業者に確認すべき内容：

- ✅ CGI はルートディレクトリで実行可能か？
- ✅ CGI を実行するには特別な設定が必要か？
- ✅ CGI は `cgi-bin/` ディレクトリのみか？
- ✅ Perl のバージョンと場所は？

---

## 修正手順

### 方法 1: FileZilla でパーミッション設定

1. **FileZilla を開く**
2. **postmail.cgi を右クリック** → 「ファイルのプロパティ」
3. **チェックボックスを設定**：
   - Owner: [x] Read [x] Write [x] Execute
   - Group: [x] Read [ ] Write [x] Execute  
   - Other: [x] Read [ ] Write [x] Execute
4. **OK** をクリック
5. **init.cgi と check.cgi** も同じ設定

### 方法 2: SSH でパーミッション設定

SSH でサーバーにアクセスできる場合：

```bash
cd /（ドキュメントルート）
chmod 755 postmail.cgi init.cgi check.cgi
ls -la postmail.cgi    # 確認: -rwxr-xr-x
```

### 方法 3: postmail.cgi の Perl パスを修正

1. テキストエディタで `postmail.cgi` を開く
2. **最初の行**を確認：
   ```perl
   #!/usr/local/bin/perl
   ```
3. サーバーの Perl パスに変更（例）：
   ```perl
   #!/usr/bin/perl
   ```
4. 再度 FTP でアップロード（**バイナリモード**）

---

## テスト方法

### check.cgi で CGI 実行可能か確認

1. ブラウザを開く
2. URL を入力：
   ```
   https://be-intl.com/check.cgi
   ```
3. ページが表示されればCGI 実行可能 ✅
4. テキストが表示されれば CGI 実行不可 ❌

---

## よくある原因と対策

| 症状 | 原因 | 対策 |
|------|------|------|
| CGI のテキストが表示される | パーミッション設定なし | `chmod 755` |
| 500 エラー | Perl パスが間違っている | シェバン行を修正 |
| 403 Forbidden | CGI 実行禁止 | ホスティング業者に相談 |
| 404 Not Found | ファイルが見つからない | ファイル場所を確認 |

---

## ホスティング業者への問い合わせ例

**件名**: CGI スクリプト実行の設定について

**本文**:
```
いつもお世話になっています。
Perl CGI スクリプトをアップロードしましたが、実行されずにテキストが表示されます。

■ 環境確認
- ドキュメントルート直下に postmail.cgi を配置
- パーミッションを 755 に設定済み
- Perl シェバン: #!/usr/local/bin/perl

■ 質問
1. ドキュメントルート直下で CGI を実行可能ですか？
2. CGI を実行するには特別な設定が必要ですか？
3. Perl のパスは `/usr/local/bin/perl` で合っていますか？

よろしくお願いします。
```

---

## 次のステップ

1. **check.cgi にアクセス** して CGI 実行可能か確認
2. **パーミッション** を 755 に設定
3. それでも動かない場合は **ホスティング業者に問い合わせ**
