function toggleFav(btn) {
    const key = btn.dataset.key;
    let favs = JSON.parse(localStorage.getItem('favorites') || '[]');
    if (favs.includes(key)) {
        favs = favs.filter(k => k !== key);
        btn.textContent = '☆';
        btn.classList.remove('fav-active');
    } else {
        favs.push(key);
        btn.textContent = '★';
        btn.classList.add('fav-active');
    }
    localStorage.setItem('favorites', JSON.stringify(favs));
}

function initFavs() {
    const favs = new Set(JSON.parse(localStorage.getItem('favorites') || '[]'));
    document.querySelectorAll('.idol-fav-btn').forEach(btn => {
        if (favs.has(btn.dataset.key)) {
            btn.textContent = '★';
            btn.classList.add('fav-active');
        }
    });
}
