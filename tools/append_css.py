import os

css1 = """
/* 属性表記（H1） */
.taiken-head__attr {
  font-family: "Noto Serif JP", "Yu Mincho", "MS Mincho", serif;
  font-size: 0.75em;
  font-weight: 400;
  margin-left: 0.5em;
}
"""

css2 = """
/* 属性表記（テーブル） */
.taiken-index__attr {
  font-family: "Noto Serif JP", "Yu Mincho", "MS Mincho", serif;
  font-size: 0.85em;
  font-weight: 400;
  margin-left: 0.3em;
  color: #6b7280;
}
"""

with open('assets/css/taiken-article.css', 'a', encoding='utf-8') as f:
    f.write(css1)

with open('assets/css/voices.css', 'a', encoding='utf-8') as f:
    f.write(css2)

print("CSS appended.")
