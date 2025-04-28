document.addEventListener('DOMContentLoaded', function() {
    const bannerTitle = document.querySelector('.banner_title');
    bannerTitle.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

    const scrollToTopBtn = document.getElementById('scrollToTopBtn');
    window.addEventListener('scroll', () => {
        scrollToTopBtn.style.display = window.scrollY > 300 ? 'block' : 'none';
    });

    scrollToTopBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
});

function saveTableAsImage(tableId) {
    const table = document.getElementById(tableId);
    if (!table) {
        console.error('テーブルが見つかりません: ', tableId);
        return;
    }

    html2canvas(table).then(canvas => {
        const link = document.createElement('a');
        link.download = 'idol_birthday.png';
        link.href = canvas.toDataURL();
        link.click();
    }).catch(err => console.error('画像の生成に失敗しました: ', err));
}