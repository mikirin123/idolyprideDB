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

    // キャラごとのチェック・解除ボタン機能
    const characterCategories = document.querySelectorAll('.character-category');
    characterCategories.forEach(category => {
        const checkAllButton = category.querySelector('.check-all');
        const uncheckAllButton = category.querySelector('.uncheck-all');
        const idolItems = category.querySelectorAll('.idol-item');

        checkAllButton.addEventListener('click', function() {
            idolItems.forEach(item => item.classList.add('owned'));
        });

        uncheckAllButton.addEventListener('click', function() {
            idolItems.forEach(item => item.classList.remove('owned'));
        });
    });

    // チェック結果を共有する機能
    const shareButton = document.getElementById('shareButton');
    shareButton.addEventListener('click', function() {
        const ownedItems = [];
        document.querySelectorAll('.idol-item.owned').forEach(item => {
            const charName = item.closest('.character-category').id;
            const cardName = item.querySelector('span').textContent.split('\n')[0];
            ownedItems.push(`${charName} - ${cardName}`);
        });

        const shareData = {
            title: '所持キャラリスト',
            text: `私の所持キャラリスト:\n${ownedItems.join('\n')}`,
        };

        if (navigator.share) {
            navigator.share(shareData).catch(err => console.error('共有に失敗しました:', err));
        } else {
            alert('共有機能がサポートされていません。以下をコピーしてください:\n\n' + shareData.text);
        }
    });
});