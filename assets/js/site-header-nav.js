/**
 * 固定ヘッダー: モバイルメニュー開閉、Escape、ボタンラベル（aria 補足）
 * 使用: トップ（index.html）、test2 等 data-menu-btn / #primary-nav を持つページ
 */
(function () {
  'use strict';
  var header = document.querySelector('.site-header');
  var btn = document.querySelector('[data-menu-btn]');
  var nav = document.getElementById('primary-nav');
  if (!header || !btn || !nav) return;

  var labelOpen = 'メニューを開く';
  var labelClose = 'メニューを閉じる';
  var hiddenSpan = btn.querySelector('.visually-hidden');

  function setOpen(open) {
    header.classList.toggle('is-menu-open', open);
    btn.setAttribute('aria-expanded', open);
    if (hiddenSpan) {
      hiddenSpan.textContent = open ? labelClose : labelOpen;
    }
  }

  btn.addEventListener('click', function () {
    setOpen(!header.classList.contains('is-menu-open'));
  });

  nav.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function () {
      setOpen(false);
    });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && header.classList.contains('is-menu-open')) {
      setOpen(false);
      btn.focus();
    }
  });
})();
