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
    // html2canvasの非同期処理が終わってからwindow.openすると「ユーザー操作起因」と
    // 認識されずスマホブラウザにブロックされるため、クリック直後・同期的にタブを開いておく
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    const newTab = isMobile ? window.open('', '_blank') : null;
    if (newTab) newTab.document.write('画像を生成中です…しばらくお待ちください。');

    html2canvas(table)
        .then(canvas => finishImageSave(canvas, 'idol_color.png', newTab))
        .catch(err => {
            console.error('画像の生成に失敗しました:', err);
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