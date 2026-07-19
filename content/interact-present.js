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

    html2canvas(content)
        .then(canvas => shareOrDownloadCanvas(canvas, 'interact-present.png'))
        .catch(err => {
            console.error('画像の生成に失敗しました: ', err);
        });
}

// スマホでは <a download> が機能しない/信頼できないため、
// 対応端末では共有シート経由で保存、それ以外は新しいタブで開いて長押し保存してもらう
function shareOrDownloadCanvas(canvas, filename) {
    canvas.toBlob(blob => {
        if (!blob) return;
        const file = new File([blob], filename, { type: 'image/png' });
        if (navigator.canShare && navigator.canShare({ files: [file] })) {
            navigator.share({ files: [file] }).catch(() => {});
            return;
        }
        const url = URL.createObjectURL(blob);
        const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
        if (isMobile) {
            window.open(url, '_blank');
        } else {
            const link = document.createElement('a');
            link.download = filename;
            link.href = url;
            link.click();
        }
        setTimeout(() => URL.revokeObjectURL(url), 30000);
    }, 'image/png');
}