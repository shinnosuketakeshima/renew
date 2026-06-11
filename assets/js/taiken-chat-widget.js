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

    // Example prompts (in Japanese)
    this.examplePrompts = [
      "📍 スリランカの安全性",
      "💰 費用について",
      "👥 一人参加の不安",
      "🏡 ホームステイの環境",
      "📚 英語レッスンについて"
    ];

    this.init();
  }

  init() {
    this.createWidgetDOM();
    this.attachEventListeners();
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
            <p>「どんなことが知りたい？」</p>
            <div class="taiken-chat__examples">
              ${this.examplePrompts.map(prompt =>
                `<button class="taiken-chat__example">${prompt}</button>`
              ).join("")}
            </div>
          </div>
        </div>
        <div class="taiken-chat__input">
          <input
            type="text"
            placeholder="質問を入力..."
            aria-label="Type your question"
          />
          <button aria-label="Send message">送信</button>
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

  toggle() {
    this.isOpen ? this.close() : this.open();
  }

  open() {
    const container = document.querySelector(".taiken-chat__container");
    if (container) {
      container.style.display = "flex";
      this.isOpen = true;
      if (typeof window.gtag === 'function') {
        window.gtag('event', 'chat_open', { event_category: 'chat' });
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

    if (role === "assistant" && sources.length > 0) {
      let html = `<p>${this.escapeHtml(content)}</p>`;
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
}

// Initialize widget when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    new TaikenChatWidget();
  });
} else {
  new TaikenChatWidget();
}
