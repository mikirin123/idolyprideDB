document.addEventListener('DOMContentLoaded', function() {
    const bannerTitle = document.querySelector('.banner_title');
    bannerTitle.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // スクロールトップボタンの追加
    const scrollToTopBtn = document.getElementById('scrollToTopBtn');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            scrollToTopBtn.style.display = 'block';
        } else {
            scrollToTopBtn.style.display = 'none';
        }
    });

    scrollToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // コピー用ボタンのイベント
    document.body.addEventListener('click', function(e) {
        // コピー
        if (e.target.classList.contains('copy-info-btn')) {
            const btn = e.target;
            const name = btn.getAttribute('data-name') || '';
            const place = btn.getAttribute('data-place') || '';
            const twitter = btn.getAttribute('data-twitter') || '';
            let text = `サークル名: ${name}\n配置: ${place}`;
            if (twitter) text += `\nTwitter: ${twitter}`;
            navigator.clipboard.writeText(text).then(() => {
                btn.textContent = 'コピー済';
                setTimeout(() => { btn.textContent = 'コピー'; }, 1200);
            });
        }
        // 評価
        if (e.target.classList.contains('eval-btn')) {
            const btn = e.target;
            const states = ['-', '予', '済'];
            let current = btn.getAttribute('data-state') || '-';
            let idx = states.indexOf(current);
            idx = (idx + 1) % states.length;
            btn.setAttribute('data-state', states[idx]);
            btn.textContent = states[idx];
        }
    });
});