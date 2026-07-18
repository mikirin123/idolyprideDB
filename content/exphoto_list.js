document.addEventListener('DOMContentLoaded', function() {
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

    // スキル名クリックで詳細トグル（再クリックで隠す）
    document.querySelectorAll('.skill-name.clickable').forEach(function(cell) {
        cell.addEventListener('click', function() {
            const tr = cell.closest('tr');
            const detailId = tr.getAttribute('data-detail');
            const detailRow = document.getElementById(detailId);
            if (detailRow) {
                // display: none か空文字列なら表示、そうでなければ非表示
                if (detailRow.style.display === 'none' || detailRow.style.display === '') {
                    detailRow.style.display = 'table-row';
                } else {
                    detailRow.style.display = 'none';
                }
            }
        });
    });

    // 目次クリック時にスムーズスクロール
    document.querySelectorAll('.toc-btn-wrap').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            const href = btn.getAttribute('href');
            if (href && href.startsWith('#char-')) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
    });
});