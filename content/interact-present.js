document.addEventListener('DOMContentLoaded', function() {
    const bannerTitle = document.querySelector('.banner_title');
    bannerTitle.addEventListener('click', function() {
        location.href = '../index.html';
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
});

function saveTableAsImage() {
    const content = document.querySelector('.content'); // 修正: class="content"を取得

    // html2canvasの非同期処理が終わってからwindow.openすると「ユーザー操作起因」と
    // 認識されずスマホブラウザにブロックされるため、クリック直後・同期的にタブを開いておく
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    const newTab = isMobile ? window.open('', '_blank') : null;
    if (newTab) newTab.document.write('画像を生成中です…しばらくお待ちください。');

    html2canvas(content)
        .then(canvas => finishImageSave(canvas, 'interact-present.png', newTab))
        .catch(err => {
            console.error('画像の生成に失敗しました: ', err);
            if (newTab) newTab.close();
        });
}

function finishImageSave(canvas, filename, preOpenedTab) {
    canvas.toBlob(blob => {
        if (!blob) {
            if (preOpenedTab) preOpenedTab.close();
            return;
        }
        const url = URL.createObjectURL(blob);
        if (preOpenedTab) {
            preOpenedTab.location.href = url;
        } else {
            const link = document.createElement('a');
            link.download = filename;
            link.href = url;
            link.click();
        }
        setTimeout(() => URL.revokeObjectURL(url), 30000);
    }, 'image/png');
}