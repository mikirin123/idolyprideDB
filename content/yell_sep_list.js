document.addEventListener('DOMContentLoaded', function() {
    const bannerTitle = document.querySelector('.banner_title');
    bannerTitle.addEventListener('click', function() {
        location.href = '../index.html';
    });

    const scrollToTopBtn = document.getElementById('scrollToTopBtn');
    window.addEventListener('scroll', function() {
        scrollToTopBtn.style.display = window.scrollY > 300 ? 'block' : 'none';
    });
    scrollToTopBtn.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    initFavs();
});