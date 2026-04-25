document.addEventListener('DOMContentLoaded', () => {

  // スマホサイトへのリダイレクト
  const ua = navigator.userAgent;
  if (sessionStorage && !sessionStorage.getItem("sp_flag") &&
    (ua.indexOf('iPhone') > 0 || ua.indexOf('iPod') > 0 || ua.indexOf('Android') > 0)) {
    if (confirm('スマートフォン用サイトを表示しますか？')) {
      location.href = 'https://be-intl.com/m/volunteers.htm';
    } else {
      sessionStorage.setItem("sp_flag", true);
    }
  }

  // 画像ボタンのホバーエフェクト
  // <img>タグを使用するボタン
  const imageButtons = document.querySelectorAll('img[data-hover-src]');
  imageButtons.forEach(img => {
    const normalSrc = img.src;
    const hoverSrc = img.getAttribute('data-hover-src');

    img.addEventListener('mouseover', () => {
      img.src = hoverSrc;
    });

    img.addEventListener('mouseout', () => {
      img.src = normalSrc;
    });
  });

  // CSSで背景画像を使用するボタン
  const bgButtons = document.querySelectorAll('.nav-button, .menu-button');
  bgButtons.forEach(button => {
    const normalImg = button.getAttribute('data-normal');
    const hoverImg = button.getAttribute('data-hover');

    button.style.backgroundImage = `url(${normalImg})`;

    button.addEventListener('mouseover', () => {
      button.style.backgroundImage = `url(${hoverImg})`;
    });

    button.addEventListener('mouseout', () => {
      button.style.backgroundImage = `url(${normalImg})`;
    });
  });

});