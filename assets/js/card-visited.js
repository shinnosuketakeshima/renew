(function () {
  var KEY = 'be-intl-visited-cards';
  var visited = {};
  try { visited = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) {}

  function initCard(card) {
    var link = card.tagName === 'A' ? card : card.querySelector('a[href]');
    if (!link) return;
    var href = link.getAttribute('href');
    if (!href) return;

    var cls = card.classList[0] + '--visited';
    if (visited[href]) card.classList.add(cls);

    link.addEventListener('click', function () {
      card.classList.add(cls);
      visited[href] = true;
      try { localStorage.setItem(KEY, JSON.stringify(visited)); } catch (e) {}
    });
  }

  ['.voice-card', '.home-voices-teaser__card', '.report-index__card'].forEach(function (sel) {
    document.querySelectorAll(sel).forEach(initCard);
  });
})();
