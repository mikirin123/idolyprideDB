function toggleFavorite(btn) {
    const key = btn.dataset.key;
    let favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    if (favorites.includes(key)) {
        favorites = favorites.filter(k => k !== key);
        btn.textContent = '☆';
        btn.classList.remove('fav-active');
    } else {
        favorites.push(key);
        btn.textContent = '★';
        btn.classList.add('fav-active');
    }
    localStorage.setItem('favorites', JSON.stringify(favorites));
}

document.addEventListener('DOMContentLoaded', function() {
    const favBtn = document.getElementById('detail-fav-btn');
    if (favBtn) {
        const favorites = new Set(JSON.parse(localStorage.getItem('favorites') || '[]'));
        if (favorites.has(favBtn.dataset.key)) {
            favBtn.textContent = '★';
            favBtn.classList.add('fav-active');
        }
        favBtn.addEventListener('click', () => toggleFavorite(favBtn));
    }
});