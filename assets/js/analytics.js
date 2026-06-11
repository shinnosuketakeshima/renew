(function () {
  'use strict';

  function sendEvent(name, params) {
    if (typeof window.gtag !== 'function') return;
    window.gtag('event', name, params);
  }

  // 資料請求CTAボタン クリック
  document.addEventListener('click', function (e) {
    var el = e.target.closest('a.btn--accent, a[href="postmail.html"], a[href*="postmail"]');
    if (!el) return;
    sendEvent('cta_click', {
      event_category: 'conversion',
      event_label: el.textContent.trim().substring(0, 50),
      link_url: el.href
    });
  });

  // ナビリンク クリック
  document.addEventListener('click', function (e) {
    var el = e.target.closest('.site-nav a');
    if (!el) return;
    sendEvent('nav_click', {
      event_category: 'navigation',
      event_label: el.textContent.trim(),
      link_url: el.href
    });
  });

  // 外部リンク クリック
  document.addEventListener('click', function (e) {
    var el = e.target.closest('a[href^="http"]');
    if (!el || el.hostname === location.hostname) return;
    sendEvent('click', {
      event_category: 'outbound',
      event_label: el.href,
      transport_type: 'beacon'
    });
  });

  // スクロール深度 (25 / 50 / 75 / 90%)
  var milestones = [25, 50, 75, 90];
  var reached = {};
  window.addEventListener('scroll', function () {
    var pct = (window.scrollY + window.innerHeight) / document.documentElement.scrollHeight * 100;
    milestones.forEach(function (m) {
      if (!reached[m] && pct >= m) {
        reached[m] = true;
        sendEvent('scroll_depth', {
          event_category: 'engagement',
          event_label: m + '%',
          value: m
        });
      }
    });
  }, { passive: true });

  // チャット 体験談リンク クリック
  document.addEventListener('click', function (e) {
    var el = e.target.closest('a[data-chat-source]');
    if (!el) return;
    sendEvent('chat_source_click', {
      event_category: 'chat',
      event_label: el.getAttribute('data-chat-source').substring(0, 100),
      link_url: el.href
    });
  });

  // 資料請求フォーム 送信（postmail.html）
  var form = document.querySelector('form.postmail-form, form[action*="postmail"]');
  if (form) {
    form.addEventListener('submit', function () {
      sendEvent('generate_lead', {
        event_category: 'conversion',
        event_label: 'postmail_form_submit'
      });
    });
  }
})();
