(function () {
  'use strict';

  var GA_LEAD_KEY = 'ga_lead_sent';

  function sendEvent(name, params) {
    if (typeof window.gtag !== 'function') return;
    window.gtag('event', name, params || {});
  }

  function isThanksPage() {
    return /thanks\.html$/i.test(location.pathname) || /\/thanks\/?$/i.test(location.pathname);
  }

  // 送信完了ページ（キーイベント: generate_lead）
  if (isThanksPage()) {
    if (!sessionStorage.getItem(GA_LEAD_KEY)) {
      sessionStorage.setItem(GA_LEAD_KEY, '1');
      sendEvent('generate_lead', {
        method: 'postmail',
        page_location: location.href
      });
    }
  }

  // 資料請求CTAボタン クリック（キーイベント: cta_click）
  document.addEventListener('click', function (e) {
    var el = e.target.closest(
      'a.site-header__cta, a.btn--accent[href*="postmail"], a[href="postmail.html"], a[href$="/postmail.html"]'
    );
    if (!el) return;

    var href = el.getAttribute('href') || '';
    if (href.indexOf('postmail') === -1 && !el.classList.contains('site-header__cta')) return;
    if (/postmail\.html$/i.test(location.pathname) && href.indexOf('postmail') !== -1) return;

    sendEvent('cta_click', {
      link_text: (el.textContent || '').trim().substring(0, 50),
      link_url: el.href,
      page_location: location.href
    });
  });

  // ナビリンク クリック
  document.addEventListener('click', function (e) {
    var el = e.target.closest('.site-nav a');
    if (!el) return;
    sendEvent('nav_click', {
      link_text: (el.textContent || '').trim(),
      link_url: el.href
    });
  });

  // 外部リンク クリック
  document.addEventListener('click', function (e) {
    var el = e.target.closest('a[href^="http"]');
    if (!el || el.hostname === location.hostname) return;
    sendEvent('click', {
      link_url: el.href,
      outbound: true,
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
          percent_scrolled: m
        });
      }
    });
  }, { passive: true });

  // チャット 体験談リンク クリック
  document.addEventListener('click', function (e) {
    var el = e.target.closest('a[data-chat-source]');
    if (!el) return;
    sendEvent('chat_source_click', {
      chat_source: el.getAttribute('data-chat-source').substring(0, 100),
      link_url: el.href
    });
  });
})();
