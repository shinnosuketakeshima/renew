/**
 * FAQ アコーディオン制御
 * [data-faq-accordion] 内のボタンをクリックして回答を開閉する
 */
(function () {
  'use strict';

  var containers = document.querySelectorAll('[data-faq-accordion]');
  if (!containers.length) return;

  containers.forEach(function (container) {
    container.addEventListener('click', function (e) {
      var trigger = e.target.closest('.faq-accordion__trigger');
      if (!trigger) return;

      var panelId = trigger.getAttribute('aria-controls');
      var panel = document.getElementById(panelId);
      var item = trigger.closest('.faq-accordion__item');

      var isExpanded = trigger.getAttribute('aria-expanded') === 'true';

      // 状態の切り替え
      trigger.setAttribute('aria-expanded', !isExpanded);
      if (panel) {
        panel.hidden = isExpanded;
      }
      if (item) {
        item.classList.toggle('is-open', !isExpanded);
      }
    });
  });
})();
