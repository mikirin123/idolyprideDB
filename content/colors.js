document.addEventListener('DOMContentLoaded', () => {
    const bannerTitle = document.querySelector('.banner_title');
    const scrollToTopBtn = document.getElementById('scrollToTopBtn');

    bannerTitle.addEventListener('click', () => {
        location.href = '../index.html';
    });

    window.addEventListener('scroll', () => {
        scrollToTopBtn.style.display = window.scrollY > 300 ? 'block' : 'none';
    });

    scrollToTopBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
});

function copyColorCode(colorCode, characterName) {
    navigator.clipboard.writeText(colorCode)
        .then(() => alert(`${characterName}のカラーコードをコピーしました！`))
        .catch(err => console.error('コピーに失敗しました:', err));
}

function saveTableAsImage() {
    const table = document.getElementById('color_table');
    html2canvas(table)
        .then(canvas => shareOrDownloadCanvas(canvas, 'idol_color.png'))
        .catch(err => console.error('画像の生成に失敗しました:', err));
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