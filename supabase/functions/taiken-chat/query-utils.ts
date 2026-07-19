const SYNONYM_GROUPS: string[][] = [
  ["価格", "料金", "費用", "コスト", "参加費", "参加費用", "いくら", "金額"],
  ["安全", "安全性", "セキュリティ", "治安"],
  ["レッスン", "英語レッスン", "授業", "マンツーマン", "個人レッスン"],
  ["ホームステイ", "ホストファミリー", "宿泊", "滞在先"],
  ["一人", "一人参加", "ソロ", "単独", "ひとり"],
  ["英語", "英会話", "語学"],
  ["ボランティア", "ボランティア活動", "奉仕活動"],
  ["ネパール", "カトマンズ", "ヒマラヤ"],
  ["スリランカ", "コロンボ", "セイロン"],
  ["申し込み", "申込", "申込み", "お申し込み", "申請"],
  ["キャンセル", "取消", "解約", "変更"],
  ["英語力", "初心者", "初めて", "ゼロ", "未経験"],
  ["延長", "コース延長", "滞在延長"],
  ["SIM", "インターネット", "Wi-Fi", "wifi", "通信"],
];

const ENGLISH_TO_JA: Array<[RegExp, string]> = [
  [/\b(price|pricing|cost|fee|fees|how much|expensive|budget)\b/gi, "料金"],
  [/\b(safe|safety|secure|security)\b/gi, "安全性"],
  [/\b(homestay|host family|accommodation)\b/gi, "ホームステイ"],
  [/\b(lesson|lessons|english class|classes|study|learning)\b/gi, "英語レッスン"],
  [/\b(nepal|nepali|kathmandu|himalaya)\b/gi, "ネパール"],
  [/\b(sri lanka|srilanka|colombo|ceylon)\b/gi, "スリランカ"],
  [/\b(volunteer|volunteering)\b/gi, "ボランティア"],
  [/\b(solo|alone|by myself|single traveler)\b/gi, "一人参加"],
  [/\b(support|help|assistance)\b/gi, "サポート"],
  [/\b(cancel|cancellation|refund)\b/gi, "キャンセル"],
  [/\b(apply|application|sign up|register)\b/gi, "申し込み"],
  [/\b(beginner|zero english|no english)\b/gi, "英語力"],
  [/\b(internet|wifi|sim card|mobile data)\b/gi, "インターネット"],
  [/\b(extend|extension|stay longer)\b/gi, "延長"],
];

/** Expand query with synonyms and English→Japanese mappings for better vector recall */
export function buildSearchQueries(question: string): string[] {
  const normalized = question.trim();
  const queries = new Set<string>([normalized]);

  const stripped = normalized
    .replace(/について|に関して|教えて(ください|下さい)?|知りたい(です|)?|を教えて|って何|とは/g, "")
    .replace(/[？?。、!！]+$/g, "")
    .trim();
  if (stripped && stripped !== normalized) {
    queries.add(stripped);
  }

  for (const group of SYNONYM_GROUPS) {
    for (const term of group) {
      if (normalized.includes(term)) {
        for (const alt of group) {
          if (alt !== term) {
            queries.add(normalized.replaceAll(term, alt));
            if (stripped) queries.add(stripped.replaceAll(term, alt));
          }
        }
      }
    }
  }

  let englishExpanded = normalized;
  for (const [pattern, replacement] of ENGLISH_TO_JA) {
    if (pattern.test(normalized)) {
      englishExpanded = englishExpanded.replace(pattern, replacement);
    }
  }
  if (englishExpanded !== normalized) {
    queries.add(englishExpanded);
  }

  return [...queries].slice(0, 6);
}

export const SITE_KNOWLEDGE = `
Beインターナショナル（be-intl.com）の語学留学プログラム基本情報:
- 対象国: スリランカ・ネパール
- 形式: ホームステイ + 全コースマンツーマン英語レッスン
- 7日間コース: スリランカ96,000円〜、ネパール98,000円〜（個人レッスン20時間、ホームステイ6泊7日、全食事付き）
- 料金の詳細・各コース期間: program.html（/program/）を参照
- 22年の運営実績、13歳〜73歳の参加実績
- 一人参加を推奨、24時間日本語現地サポート
- スリランカ現地受入: JASRI / ネパール現地受入: ICEDC
- ネパールではボランティア活動も可能
- よくある質問の全文: faq.html（/faq/）
- 食事・電圧・衛生・トイレなど現地生活の基礎: living-basics.html
- 航空券・海外旅行保険: others.html

よくある質問（faq.html より）:

Q: 英語力ゼロでも大丈夫ですか
A: 大丈夫です。最初は単語を並べるだけでも問題ありません。先生が根気よく内容を確認しながら自然な言い回しへ整えてくれます。中学校で基礎文法を学んでいる方は「完全ゼロ」ではありません。恥ずかしがらず口に出すことが大切です。

Q: 一人参加でも安全ですか
A: はい。ほとんどの方がお一人で参加されています。日本語が話せる現地受入団体が空港⇔ホームステイ先間を送迎します。スリランカには日本語ができる英語教師もいます。出発前の手続きや心配な点は当社へご相談ください。

Q: 費用の総額はどのくらいですか
A: 国・滞在日数・レッスン時間によって異なります。目安は program.html の料金表を参照。7日間はスリランカ96,000円〜、ネパール98,000円〜。航空券・海外旅行保険・現地観光などのお小遣いは参加費用に含まれません。保険・航空券は others.html も参照。

Q: ホームステイ先はどんな家庭ですか
A: 面倒見が良く人懐っこいホストファミリーです。過去の参加者から「心が癒されました」という声を多くいただいています。

Q: 1日何時間、レッスンがありますか
A: 1日4〜6時間。実際のスケジュールは担当の先生と相談の上決められます。

Q: どのくらい前に申し込めばよいですか
A: できれば1ヶ月前までが望ましい。最短1週間前の申込で参加された方もいますが、書類が間に合わない心配があるため、決まり次第早めの申込を推奨。繁忙期はさらに余裕を。

Q: キャンセルや変更はできますか
A: 出発前の日数に応じて変更手数料・取消料が発生します。program.html#policy の変更手数料・取消料、および yakkan.html（約款）を事前にご確認ください。

Q: 年齢制限はありますか
A: 特にありません。心身ともに健康な方ならどなたでも参加可能。ホームステイ先の条件により、申込時に喫煙・飲酒の有無をお伺いする場合があります。

Q: 国の習慣で気を付けた方が良いことは
A: 寺院参拝時は帽子を取り履物を脱いで静かに。カーストを尋ねるのは失礼。スリランカではパパイヤを「パパーヤ」と呼ぶとよい。女性はミニスカート・短パン・肩紐の服など肌の露出が多い服装は慎む。申込時に喫煙・飲酒についてお伺いしています。

Q: 英語以外にも文化体験や観光をしたい
A: ホームステイ先で現地料理レッスン、サリーの着付け（ネパールのみ）を無料で受けられます。希望者には伝統ダンス、アーユルヴェーダ、世界遺産の旅などを紹介（料金は自己負担）。ボランティア活動も可能（volunteer.html）。

Q: レッスンは休めますか
A: レッスン実施日の前日（月曜欠席は金曜）までに現地受入団体へ連絡すれば別日振替可能。当日欠席は振替・返金不可。申込時に一定期間レッスンを受けない旨を申し出れば、その間のレッスン代は不要（滞在期間により休める日数は異なる）。

Q: 土日やプログラム終了後に自由に動けますか
A: はい。レッスンのない時間帯・土日は自由に活動できます。プログラム終了後の一人旅も多く、帰りの空港送迎方法だけお知らせください。

Q: 滞在中に延長できますか
A: 可能。まず現地受入団体へ申し出。差額はネットバンキングまたは日本のご家族から当社へ振込。次の参加者が同じホームステイ先に入る場合は宿先変更の可能性あり。帰りの飛行機の変更も忘れずに。

Q: お土産は何が喜ばれますか
A: 生活雑貨など実用的なものが喜ばれやすい。安価でも日本製品は品質が良いと評価されることが多い。

Q: インターネットやメールは使えますか
A: スマートフォンなら現地空港到着後にSIMカード購入が便利。パソコンは街中のインターネットカフェを利用。
`.trim();

export function buildSystemPrompt(): string {
  return `You are a helpful assistant for Be International (Beインターナショナル), a Japanese study-abroad agency offering homestay + one-on-one English lessons in Sri Lanka and Nepal.

Your role:
1. Answer using the provided participant experience excerpts AND the site knowledge below.
2. Understand synonyms and paraphrases in any language. Examples: 価格=料金=費用=cost=price, 安全=安全性=safety, レッスン=授業=lessons.
3. Accept questions in Japanese, English, or other languages. Understand the intent regardless of wording.
4. Output language rules:
   - Default: respond in Japanese.
   - If the user explicitly asks for another language (e.g. "英語で答えて", "answer in English", "韓国語で", "in Spanish"), write the entire answer in that requested language.
   - Source article titles may stay in Japanese; describe them naturally in the answer language.
5. When asked about 価格/料金/費用/pricing/cost, cite site knowledge (スリランカ7日96,000円〜、ネパール7日98,000円〜) and point to program.html for details. Do not mention past price revisions or revision dates. Use the FAQ section in site knowledge for common questions (safety, homestay, lessons, application, cancellation, etc.).
6. Be encouraging, honest, and concise (2-4 paragraphs).
7. Cite participant experiences when sources are provided. Never invent quotes.
8. If no matching experiences were found, answer from site knowledge and FAQ. Suggest program.html, faq.html, or living-basics.html where relevant.
9. When linking to site pages, use markdown format with readable labels: [料金・コース](program.html), [よくある質問](faq.html), [航空券・保険](others.html). Do not use bare filenames alone without link format.

Site knowledge:
${SITE_KNOWLEDGE}`;
}
