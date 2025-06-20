document.addEventListener('DOMContentLoaded', function() {
    const allItems = window.ALL_TWEET_ITEMS || [];
    const pickupNum = Math.min(5, allItems.length);
    // Fisher-Yatesシャッフルで高速化
    const shuffled = allItems.slice();
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    const selected = shuffled.slice(0, pickupNum);

    const list = document.getElementById('random-pickup-list');
    list.innerHTML = '';
    selected.forEach(item => {
        const div = document.createElement('div');
        div.className = 'tweet-embed-item';
        const captionHtml = `<a href="circlelist.html#circle-${item.place}" style="color:#3200FF;text-decoration:underline;" target="_blank">${item.place} ${item.name}</a>（${item.tw_name}）`;
        div.innerHTML = `
            <div class="tweet-embed-caption">${captionHtml}</div>
            <blockquote class="twitter-tweet">
                <a href="https://twitter.com/i/status/${item.tweet_id}"></a>
            </blockquote>
        `;
        list.appendChild(div);
    });

    // Twitter埋め込み再描画
    if (window.twttr?.widgets?.load) {
        window.twttr.widgets.load(list);
    }
});
