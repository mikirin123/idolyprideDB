document.addEventListener('DOMContentLoaded', () => {
    if (!window.twttr) {
        const s = document.createElement('script');
        s.src = "https://platform.twitter.com/widgets.js";
        s.async = true;
        document.head.appendChild(s);
    }

    const embedTweet = el => {
        if (el.dataset.loaded) return;
        el.dataset.loaded = "1";
        const tweetId = el.dataset.tweetId;
        if (!tweetId) return;
        const tryEmbed = () => {
            if (window.twttr?.widgets) {
                window.twttr.widgets.createTweet(tweetId, el, { align: "center" });
            } else {
                setTimeout(tryEmbed, 500);
            }
        };
        tryEmbed();
    };

    const tweetNodes = document.querySelectorAll('.tweet-lazy-embed');
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    embedTweet(entry.target);
                    obs.unobserve(entry.target);
                }
            });
        }, { rootMargin: "200px" });
        tweetNodes.forEach(el => observer.observe(el));
    } else {
        tweetNodes.forEach(embedTweet);
    }
});