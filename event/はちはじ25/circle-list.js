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
    window.addEventListener('scroll', () => {
        scrollToTopBtn.style.display = window.scrollY > 300 ? 'block' : 'none';
    });
    scrollToTopBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // localStorage操作
    const storageKey = 'circleEval';
    const getEvalStorage = () => {
        try { return JSON.parse(localStorage.getItem(storageKey)) || {}; } catch { return {}; }
    };
    const setEvalStorage = data => localStorage.setItem(storageKey, JSON.stringify(data));

    // 評価ボタン初期化
    const evalStates = getEvalStorage();
    document.querySelectorAll('.eval-btn').forEach(btn => {
        const key = btn.closest('tr')?.id || '';
        if (evalStates[key]) {
            btn.setAttribute('data-state', evalStates[key]);
            btn.textContent = evalStates[key];
        }
    });

    // コピー・評価イベント委譲
    document.body.addEventListener('click', e => {
        if (e.target.classList.contains('copy-info-btn')) {
            const btn = e.target;
            const name = btn.getAttribute('data-name') || '';
            const place = btn.getAttribute('data-place') || '';
            const twitter = btn.getAttribute('data-twitter') || '';
            let text = `サークル名: ${name}\n配置: ${place}`;
            if (twitter) text += `\nTwitter: ${twitter}`;
            navigator.clipboard.writeText(text).then(() => {
                btn.textContent = 'コピー済';
                setTimeout(() => { btn.textContent = 'コピー'; }, 1200);
            });
        }
        if (e.target.classList.contains('eval-btn')) {
            const btn = e.target;
            const states = ['-', '予', '済'];
            let idx = (states.indexOf(btn.getAttribute('data-state') || '-') + 1) % states.length;
            btn.setAttribute('data-state', states[idx]);
            btn.textContent = states[idx];
            const key = btn.closest('tr')?.id || '';
            const evalStates = getEvalStorage();
            if (states[idx] === '-') delete evalStates[key];
            else evalStates[key] = states[idx];
            setEvalStorage(evalStates);
        }
    });
});