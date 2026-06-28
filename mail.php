<?php
/**
 * Beインターナショナル 資料請求・お問い合わせ メール送信スクリプト
 */

// --- 設定 ---
// 管理者メールアドレス
$to = 'info@be-intl.com';
// メールの件名
$subject_prefix = '【資料請求・お問い合わせ】';
// 完了後のリダイレクト先
$thanks_page = 'thanks.html';
// エラー時の戻り先
$error_page = 'postmail.html';

// 文字コード設定（フォームは UTF-8。uni で mb_send_mail の JIS 変換を避ける）
mb_language('uni');
mb_internal_encoding('UTF-8');

if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    header("Location: " . $error_page);
    exit;
}

// フォームデータの取得
$data = $_POST;

// 必須項目のチェック (hidden 'need' にスペース区切りで指定されたフィールド)
$need = isset($data['need']) ? explode(' ', trim($data['need'])) : [];
$errors = [];
foreach ($need as $field) {
    if (!isset($data[$field]) || trim($data[$field]) === '') {
        $errors[] = "「{$field}」は必須項目です。";
    }
}

// メールアドレスの一致チェック (hidden 'match' に指定されたフィールド)
if (!empty($data['match'])) {
    $match_fields = explode(' ', trim($data['match']));
    if (count($match_fields) >= 2) {
        $f1 = $match_fields[0];
        $f2 = $match_fields[1];
        if (isset($data[$f1]) && isset($data[$f2]) && $data[$f1] !== $data[$f2]) {
            $errors[] = "メールアドレスが一致しません。";
        }
    }
}

// メール形式の簡易チェック
if (!empty($data['email'])) {
    $email = trim($data['email']);
    if (strpos($email, '@') === false || strpos($email, '.', strpos($email, '@')) === false) {
        $errors[] = "E-mailアドレスの形式が正しくありません。";
    }
}

// エラーがある場合はJavaScriptで通知して戻る
if (!empty($errors)) {
    echo "<script>alert('" . implode("\\n", $errors) . "'); history.back();</script>";
    exit;
}

// メールの本文作成 (hidden 'sort' の順序に従う)
$sort = isset($data['sort']) ? explode(' ', trim($data['sort'])) : array_keys($data);
$body = "資料請求・お問い合わせがありました。\n\n";
$body .= "--------------------------------------------------\n";

foreach ($sort as $field) {
    if (isset($data[$field]) && !in_array($field, ['need', 'match', 'sort', 'email2'])) {
        $val = is_array($data[$field]) ? implode(', ', $data[$field]) : $data[$field];
        $body .= "【 {$field} 】 {$val}\n";
    }
}
$body .= "--------------------------------------------------\n\n";
$body .= "送信日時: " . date("Y/m/d H:i:s") . "\n";
$body .= "送信元IP: " . $_SERVER['REMOTE_ADDR'] . "\n";

// 管理者へのメール送信
$user_name = isset($data['name']) ? $data['name'] : 'No Name';
$user_email = isset($data['email']) ? $data['email'] : '';
$subject = $subject_prefix . $user_name;

// 送信元(From)はサーバーのドメインに合わせるのが一般的（なりすまし判定回避）
// 返信先(Reply-To)にユーザーのアドレスを設定
$from_email = 'info@be-intl.com';
$headers = 'From: ' . mb_encode_mimeheader('Beインターナショナル', 'UTF-8', 'B') . " <{$from_email}>\r\n";
if (!empty($user_email)) {
    $headers .= "Reply-To: {$user_email}\r\n";
}
$headers .= "MIME-Version: 1.0\r\n";
$headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
$headers .= "Content-Transfer-Encoding: 8bit\r\n";
$headers .= 'X-Mailer: PHP/' . phpversion() . "\r\n";

$result = mb_send_mail($to, $subject, $body, $headers);

// 自動返信
if ($result && !empty($user_email)) {
    $reply_subject = "【Beインターナショナル】資料請求・お問い合わせを承りました";
    $reply_body = "{$user_name} 様\n\n";
    $reply_body .= "この度は、資料請求・お問い合わせをいただき、誠にありがとうございます。\n";
    $reply_body .= "以下の内容で承りました。\n\n";
    $reply_body .= $body;
    $reply_body .= "\n資料をご希望の方には、お送りさせていただきます。\n";
    $reply_body .= "\nお問い合わせの場合は、確認でき次第に返信させていただきます。\n";
    $reply_body .= "\n３日間経っても何も連絡がなかった場合は、何らかの理由でメールが送信されなかった可能性があります。その際には、再度送信いただきますよう、よろしくお願い致します。\n";
    $reply_body .= "\n ♪お知らせ♪

スリランカでは、４月中旬が本当のお正月になります。
ホームステイ先のホストファミリーは、親戚や友人宅の訪問や来客が相次ぎ、
日本人のお客様の対応が難しくなります。

その為、毎年４月１０日～２０日付近の、ホームステイの新たな受入れと、
レッスンはお休みさせていただいております。

その為、大変恐れ入りますが、４月にご参加をご検討の場合は、
・４月上旬から３週間以上のご参加
・４月２２日以降からのご参加
の場合のみ受付させていただきます。

４月上旬までにホームステイを開始したお客様は、お正月期間も引き続き
ホームステイしていただきますので、スリランカのお正月を是非ご体験くださ
い。
ただし、この期間はレッスンはお休みになります。

年末年始（１月１日前後）も通常通り、ホームステイおよびレッスンは行って
おりますので、お気軽にご参加ください。


◆◆・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・・
スリランカ,ネパールで英語を学ぶプログラム
Beインターナショナル
逢坂光子（おうさかみつこ）
osaka@be-intl.com
https://be-intl.com
東京都渋谷区幡ヶ谷1-23-19
サンハイムミヤタ2F 〒151-0072
TEL:03-6770-6191

";
    
    mb_send_mail($user_email, $reply_subject, $reply_body, $headers);
}

if ($result) {
    header("Location: " . $thanks_page);
    exit;
} else {
    echo "メールの送信に失敗しました。システム管理者へお問い合わせください。";
}
