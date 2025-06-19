document.addEventListener('DOMContentLoaded', function() {
    // Twitter widgets.jsがなければロード
    if (!window.twttr) {
        var s = document.createElement('script');
        s.src = "https://platform.twitter.com/widgets.js";
        s.async = true;
        document.head.appendChild(s);
    }

    function embedTweet(el) {
        if (el.dataset.loaded) return;
        el.dataset.loaded = "1";
        var tweetId = el.getAttribute('data-tweet-id');
        if (!tweetId) return;
        // 埋め込み
        if (window.twttr && window.twttr.widgets) {
            window.twttr.widgets.createTweet(tweetId, el, { align: "center" });
        } else {
            // widgets.js未ロード時は後で再試行
            setTimeout(function() { embedTweet(el); }, 500);
        }
    }

    if ('IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function(entries, obs) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    embedTweet(entry.target);
                    obs.unobserve(entry.target);
                }
            });
        }, { rootMargin: "200px" });
        document.querySelectorAll('.tweet-lazy-embed').forEach(function(el) {
            observer.observe(el);
        });
    } else {
        // Fallback: 全部埋め込む
        document.querySelectorAll('.tweet-lazy-embed').forEach(embedTweet);
    }
});
