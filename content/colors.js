document.addEventListener('DOMContentLoaded', () => {
    const bannerTitle = document.querySelector('.banner_title');
    const scrollToTopBtn = document.getElementById('scrollToTopBtn');

    bannerTitle.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
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
        .then(canvas => {
            const link = document.createElement('a');
            link.download = 'idol_color.png';
            link.href = canvas.toDataURL();
            link.click();
        })
        .catch(err => console.error('画像の生成に失敗しました:', err));
}