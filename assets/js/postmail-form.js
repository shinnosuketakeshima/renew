(function () {
  'use strict';

  var form = document.getElementById('postmail-form');
  if (!form) return;

  var emailInput = document.getElementById('postmail-email');
  if (!emailInput) return;

  function isValidEmail(value) {
    var trimmed = (value || '').trim();
    if (!trimmed) return false;
    var parts = trimmed.split('@');
    if (parts.length !== 2) return false;
    if (!parts[0] || !parts[1]) return false;
    if (parts[1].indexOf('.') === -1) return false;
    return true;
  }

  form.addEventListener('submit', function (e) {
    var email = emailInput.value.trim();

    if (!isValidEmail(email)) {
      e.preventDefault();
      alert('E-mailアドレスを正しい形式（例: name@example.com）でご入力ください。');
      emailInput.focus();
      return;
    }

    var message = 'このメールアドレスで送信します。\n\n' + email + '\n\nよろしいですか？';
    if (!window.confirm(message)) {
      e.preventDefault();
      emailInput.focus();
    }
  });
})();
