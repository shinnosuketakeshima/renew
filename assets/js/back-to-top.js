/**
 * ページ先頭へ戻る（固定表示）。 home.css の .back-to-top と併用。
 * 遅延読み込み可（defer）。長い記事・一覧の縦スクロール負担を軽減。
 */
(function () {
  'use strict';

  var showAfterPx = 360;

  var btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'back-to-top';
  btn.setAttribute('aria-label', 'ページの先頭へ戻る');
  var inner = document.createElement('span');
  inner.className = 'back-to-top__icon';
  inner.setAttribute('aria-hidden', 'true');
  inner.textContent = '↑';
  btn.appendChild(inner);
  var label = document.createElement('span');
  label.className = 'back-to-top__label';
  label.textContent = '上へ';
  btn.appendChild(label);

  function applyVisibility() {
    var y = window.scrollY || document.documentElement.scrollTop || 0;
    btn.hidden = y < showAfterPx;
  }

  var ticking = false;
  function onScroll() {
    if (!ticking) {
      window.requestAnimationFrame(function () {
        applyVisibility();
        ticking = false;
      });
      ticking = true;
    }
  }

  btn.addEventListener('click', function () {
    var reduce = false;
    try {
      reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    } catch (e) {
      /* ignore */
    }
    window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' });
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      document.body.appendChild(btn);
      applyVisibility();
      window.addEventListener('scroll', onScroll, { passive: true });
    });
  } else {
    document.body.appendChild(btn);
    applyVisibility();
    window.addEventListener('scroll', onScroll, { passive: true });
  }
})();
