/**
 * Taiken Chat Widget
 * Floating chat interface for asking questions about study abroad experiences
 */

class TaikenChatWidget {
  constructor(options = {}) {
    this.isOpen = false;
    this.messages = [];
    this.apiUrl = options.apiUrl || "https://oeqohmudfaisdnsikziy.supabase.co/functions/v1/taiken-chat";
    this.isLoading = false;

    // Example prompts
    this.examplePrompts = [
      "スリランカの安全性",
      "ネパールの安全性",
      "英語レッスンについて",
      "ホームステイの環境",
      "参加費用について"
    ];

    this.init();
  }

  init() {
    this.createWidgetDOM();
    this.attachEventListeners();
    this.attachExternalTriggers();
  }

  createWidgetDOM() {
    const widget = document.createElement("div");
    widget.id = "taiken-chat-widget";
    widget.innerHTML = `
      <button class="taiken-chat__button" aria-label="Open chat">💬</button>
      <div class="taiken-chat__container" style="display: none;">
        <div class="taiken-chat__header">
          <h3>体験者の経験から探す</h3>
          <button class="taiken-chat__close" aria-label="Close chat">×</button>
        </div>
        <div class="taiken-chat__content">
          <div class="taiken-chat__welcome">
            <div class="taiken-chat__examples">
              ${this.examplePrompts.map(prompt =>
                `<button class="taiken-chat__example">${prompt}</button>`
              ).join("")}
            </div>
          </div>
        </div>
        <div class="taiken-chat__input">
          <p class="taiken-chat__input-hint">自分の言葉で、気軽に聞いてみてください</p>
          <div class="taiken-chat__input-row">
            <input
              type="text"
              placeholder="例：一人参加でも大丈夫？食事は？"
              aria-label="知りたいことを自分の言葉で入力"
            />
            <button aria-label="Send message">送信</button>
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(widget);
  }

  attachEventListeners() {
    const button = document.querySelector(".taiken-chat__button");
    const closeBtn = document.querySelector(".taiken-chat__close");
    const input = document.querySelector(".taiken-chat__input input");
    const sendBtn = document.querySelector(".taiken-chat__input button");
    const examples = document.querySelectorAll(".taiken-chat__example");

    button?.addEventListener("click", () => this.toggle());
    closeBtn?.addEventListener("click", () => this.close());
    sendBtn?.addEventListener("click", () => this.sendMessage(input?.value || ""));

    input?.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        this.sendMessage(input.value);
      }
    });

    examples.forEach(btn => {
      btn.addEventListener("click", () => {
        const text = btn.textContent.trim();
        this.sendMessage(text);
      });
    });
  }

  attachExternalTriggers() {
    document.querySelectorAll("[data-chat-open]").forEach((el) => {
      el.addEventListener("click", (e) => {
        e.preventDefault();
        this.open(el.dataset.chatOpenLabel || "external_trigger");
      });
    });
  }

  toggle() {
    this.isOpen ? this.close() : this.open();
  }

  open(sourceLabel) {
    const container = document.querySelector(".taiken-chat__container");
    if (container) {
      container.style.display = "flex";
      this.isOpen = true;
      if (typeof window.gtag === 'function') {
        window.gtag('event', 'chat_open', {
          event_category: 'chat',
          event_label: sourceLabel || 'floating_button',
        });
      }
    }
  }

  close() {
    const container = document.querySelector(".taiken-chat__container");
    if (container) {
      container.style.display = "none";
      this.isOpen = false;
    }
  }

  async sendMessage(text) {
    if (!text.trim() || this.isLoading) return;

    this.addMessageToUI("user", text);

    if (typeof window.gtag === 'function') {
      window.gtag('event', 'chat_question', {
        event_category: 'chat',
        event_label: text.substring(0, 50)
      });
    }

    const input = document.querySelector(".taiken-chat__input input");
    if (input) input.value = "";

    this.isLoading = true;
    const sendBtn = document.querySelector(".taiken-chat__input button");
    if (sendBtn) sendBtn.disabled = true;

    const loadingEl = this.addLoadingIndicator();

    try {
      const response = await fetch(this.apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9lcW9obXVkZmFpc2Ruc2lreml5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODExMjY4ODEsImV4cCI6MjA5NjcwMjg4MX0.cfTJEJHOUmQVrizBwismc2AsXZ4d0L5-Nwhoesm_jx4"
        },
        body: JSON.stringify({ question: text })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const { answer, sources } = await response.json();
      loadingEl.remove();
      this.addMessageToUI("assistant", answer, sources);
    } catch (error) {
      console.error("Chat error:", error);
      loadingEl.remove();
      this.addMessageToUI("error", "申し訳ありません。エラーが発生しました。もう一度お試しください。");
    } finally {
      this.isLoading = false;
      if (sendBtn) sendBtn.disabled = false;
    }
  }

  addLoadingIndicator() {
    const contentEl = document.querySelector(".taiken-chat__content");
    const el = document.createElement("div");
    el.className = "taiken-chat__message taiken-chat__message--assistant";
    el.innerHTML = `<div class="taiken-chat__loading"><span></span><span></span><span></span></div>`;
    contentEl.appendChild(el);
    el.scrollIntoView({ behavior: "smooth", block: "nearest" });
    return el;
  }

  addMessageToUI(role, content, sources = []) {
    const contentEl = document.querySelector(".taiken-chat__content");
    if (!contentEl) return;

    if (this.messages.length === 0) {
      const welcome = contentEl.querySelector(".taiken-chat__welcome");
      if (welcome) welcome.remove();
    }

    const msg = document.createElement("div");
    msg.className = `taiken-chat__message taiken-chat__message--${role}`;

    if (role === "assistant") {
      let html = `<div class="taiken-chat__answer">${this.formatAnswer(content)}</div>`;

      if (sources.length > 0) {
        html += `<div class="taiken-chat__sources">`;

        sources.forEach(source => {
          html += `
            <div class="taiken-chat__source">
              <strong>${this.escapeHtml(source.title)}</strong>
              <p>${this.escapeHtml(source.excerpt)}...</p>
              <small>${source.country}${source.age ? ' / ' + source.age + '歳' : ''}${source.year ? ' / ' + source.year + '年' : ''}</small>
              <a href="${source.url}" target="_blank" rel="noopener noreferrer" data-chat-source="${this.escapeHtml(source.title)}">詳しく読む →</a>
            </div>
          `;
        });

        html += `</div>`;
      }

      msg.innerHTML = html;
    } else {
      msg.textContent = content;
    }

    contentEl.appendChild(msg);
    msg.scrollIntoView({ behavior: "smooth", block: "nearest" });

    this.messages.push({ role, content });
  }

  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  /** Site page labels for auto-linking */
  pageLabel(path) {
    const base = path.split("#")[0].replace(/\.html$/i, "").split("/").pop();
    const labels = {
      program: "料金・コース",
      faq: "よくある質問",
      others: "航空券・保険",
      "living-basics": "現地生活の基礎知識",
      yakkan: "約款",
      volunteer: "ボランティア",
      postmail: "資料請求",
      process1: "出発までの流れ",
      srilanka: "スリランカ",
      nepal: "ネパール",
      voices: "参加者の声",
      about: "会社概要",
    };
    return labels[base] || path;
  }

  normalizePageHref(href) {
    const trimmed = href.trim();
    if (!trimmed || /^javascript:/i.test(trimmed)) return null;

    if (/^https?:\/\//i.test(trimmed)) {
      try {
        const url = new URL(trimmed);
        if (url.hostname.endsWith("be-intl.com")) {
          return url.pathname.replace(/^\//, "") + url.hash;
        }
      } catch {
        return null;
      }
      return null;
    }

    const path = trimmed.replace(/^\/+/, "");
    if (/^[a-z0-9-]+\.html(?:#[\w-]+)?$/i.test(path)) return path;
    if (/^(program|faq|others|living-basics|yakkan|volunteer|postmail|process1|srilanka|nepal|voices|about)\/?$/i.test(path)) {
      return path.replace(/\/$/, "") + ".html";
    }
    return null;
  }

  formatAnswer(text) {
    let html = this.escapeHtml(text);

    // Markdown links: [label](href) → clickable anchor
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, href) => {
      const url = this.normalizePageHref(href);
      if (!url) return `[${label}](${href})`;
      const displayLabel = /\.html(?:#[\w-]+)?$/i.test(label) ? this.pageLabel(url) : label;
      return `<a href="${url}" class="taiken-chat__link">${displayLabel}</a>`;
    });

    // Standalone page filenames not already linked
    html = html.replace(
      /(?<![="'])((?:program|faq|others|living-basics|yakkan|volunteer|postmail|process1|srilanka|nepal|voices|about)\.html(?:#[\w-]+)?)(?![^<]*>)/gi,
      (match) => {
        const label = this.pageLabel(match);
        return `<a href="${match}" class="taiken-chat__link">${label}</a>`;
      }
    );

    const paragraphs = html.split(/\n{2,}/).map(p => p.replace(/\n/g, "<br>"));
    return paragraphs.map(p => `<p>${p}</p>`).join("");
  }
}

// Initialize widget when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    new TaikenChatWidget();
  });
} else {
  new TaikenChatWidget();
}
