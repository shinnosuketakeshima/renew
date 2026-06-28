(function () {
  'use strict';

  function initPostmailForm() {
    var form = document.getElementById('postmail-form');
    var emailInput = document.getElementById('postmail-email');
    var nameInput = document.getElementById('postmail-name');
    var submitBtn = document.getElementById('postmail-submit-btn');
    var confirmPanel = document.getElementById('postmail-confirm');
    var confirmName = document.getElementById('postmail-confirm-name');
    var confirmEmail = document.getElementById('postmail-confirm-email');
    var confirmBack = document.getElementById('postmail-confirm-back');
    var resetBtn = form ? form.querySelector('input[type="reset"]') : null;

    if (!form || !emailInput || !submitBtn || !confirmPanel || !confirmName || !confirmEmail) {
      return;
    }

    submitBtn.type = 'button';

    function isValidEmail(value) {
      var trimmed = (value || '').trim();
      if (!trimmed) return false;
      var parts = trimmed.split('@');
      if (parts.length !== 2) return false;
      if (!parts[0] || !parts[1]) return false;
      if (parts[1].indexOf('.') === -1) return false;
      return true;
    }

    function showConfirmPanel() {
      var name = nameInput ? nameInput.value.trim() : '';
      var email = emailInput.value.trim();

      if (!name) {
        alert('お名前をご入力ください。');
        if (nameInput) nameInput.focus();
        return;
      }

      if (!isValidEmail(email)) {
        alert('E-mailアドレスを正しい形式（例: name@example.com）でご入力ください。');
        emailInput.focus();
        return;
      }

      confirmName.textContent = name;
      confirmEmail.textContent = email;
      confirmPanel.hidden = false;
      confirmPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      var confirmSend = document.getElementById('postmail-confirm-send');
      if (confirmSend) confirmSend.focus();
    }

    function hideConfirmPanel() {
      confirmPanel.hidden = true;
    }

    submitBtn.addEventListener('click', showConfirmPanel);

    if (confirmBack) {
      confirmBack.addEventListener('click', function () {
        hideConfirmPanel();
        submitBtn.focus();
      });
    }

    if (resetBtn) {
      resetBtn.addEventListener('click', hideConfirmPanel);
    }

    form.addEventListener('submit', function (e) {
      if (confirmPanel.hidden) {
        e.preventDefault();
        showConfirmPanel();
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPostmailForm);
  } else {
    initPostmailForm();
  }
})();
