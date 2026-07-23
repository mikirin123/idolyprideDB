// ==========================
// スクロールトップボタン
// ==========================
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

window.onscroll = function() {
    const scrollToTopBtn = document.getElementById('scrollToTopBtn');
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        if (window.innerWidth > 768) {
            scrollToTopBtn.style.display = "block";
        }
    } else {
        scrollToTopBtn.style.display = "none";
    }
};

// ==========================
// ページ読み込み時の初期化処理
// ==========================
document.addEventListener('DOMContentLoaded', function() {
    // メニューの設定
    const menu = document.querySelector('.menu');
    menu.tagName = 'button'; // タグをbuttonに変更
    const menuContent = document.querySelector('.menu-content');
    const popup = document.querySelector('.popup');
    const popupHeader = document.querySelector('.popup-header');
    const popupContent = document.querySelector('.popup-content');
    const popupClose = document.querySelector('.popup-close');

    menu.addEventListener('click', function() {
        menuContent.style.display = menuContent.style.display === 'block' ? 'none' : 'block';
    });

    window.addEventListener('click', function(event) {
        if (!menu.contains(event.target)) {
            menuContent.style.display = 'none';
        }
    });

    document.querySelectorAll('.menu-content a').forEach(item => {
        item.addEventListener('click', function() {
            const menuName = this.innerText.trim();
            popupHeader.innerText = menuName; // ポップアップのヘッダーにタイトルを設定
            if (menuName === '') {
                popupContent.innerHTML = '';
                popup.style.display = 'block';
                popupOverlay.style.display = 'block';
            } else if (menuName === 'このサイトについて') {
                popupContent.innerHTML =
                    '● データ<br>' +
                    '掲載データはゲーム内、SNS等公式情報をもとにしています。手作業のため誤りや反映漏れが含まれる場合があります。<br><br>' +
                    '● 作成者<br><a href="https://x.com/miki_aipr" class="about_link">ミキ</a><br><br>改善要望・不具合報告は<br><a href="https://x.com/miki_aipr" class="about_link">twitter</a>または<a href="https://forms.gle/gM8HjG6Hzq4YxCmh9" class="about_link">Googleフォーム</a>までお願いします。';
                popup.style.display = 'block';
                popupOverlay.style.display = 'block';
            } else if (menuName === 'サンクス') {
                popupContent.innerHTML =
                    '7/19のデータ追加にご協力いただきました。<br>ありがとうございます!<br><br>' +
                    '𝒮𝓊𝑔𝒶𝓇<br>' +
                    'チョコわたるしみ<br>' +
                    'RozeN<br><br><hr>';
                popup.style.display = 'block';
                popupOverlay.style.display = 'block';
            }
        });
    });

    // ポップアップの設定
    const popupOverlay = document.querySelector('.popup-overlay');

    function closePopup() {
        popup.style.animation = 'fadeOut 0.3s ease-in-out';
        popupOverlay.style.animation = 'fadeOut 0.3s ease-in-out';
        setTimeout(() => {
            popup.style.display = 'none';
            popupOverlay.style.display = 'none';
        }, 300);
    }

    popupClose.addEventListener('click', closePopup);
    popupOverlay.addEventListener('click', closePopup);

    // ヒントアイコンの設定
    const hintIcons = document.querySelectorAll('.hint-icon');
    const hintPopups = document.querySelectorAll('.hint-popup');
    hintIcons.forEach((hintIcon, index) => {
        const hintPopup = hintPopups[index];
        hintIcon.addEventListener('click', function(event) {
            event.stopPropagation();
            hintPopup.style.display = hintPopup.style.display === 'block' ? 'none' : 'block';
        });
    });

    window.addEventListener('click', function(event) {
        hintPopups.forEach(hintPopup => {
            if (!hintPopup.contains(event.target)) {
                hintPopup.style.display = 'none';
            }
        });
    });

    const bannerTitle = document.querySelector('.banner_title');
    bannerTitle.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
});

function scrollWithOffset(event) {
    event.preventDefault(); // 通常のジャンプを止める
    const href = event.currentTarget.getAttribute("href");
    const target = document.querySelector(href);
    if (target) {
      const offset = 70; // ← ここでずらす量を調整
      const position = target.getBoundingClientRect().top + window.pageYOffset - offset;
      window.scrollTo({ top: position, behavior: 'smooth' });
    }
  }
