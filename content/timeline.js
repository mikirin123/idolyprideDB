// ==========================
// フィルターアコーディオン
// ==========================
function toggleTlFilter() {
    const body = document.getElementById('tl-filter-body');
    const icon = document.getElementById('tl-filter-toggle-icon');
    const isOpen = body.style.display !== 'none';
    body.style.display = isOpen ? 'none' : '';
    icon.textContent = isOpen ? '▼' : '▲';
}

// ==========================
// フィルターURL同期
// ==========================
function updateTlUrlParams(f) {
    const params = new URLSearchParams();
    if (f.keywords.length) params.set('q', f.keywords.join(' '));
    if (f.searchMode !== 'and') params.set('mode', f.searchMode);
    if (f.charFilter) params.set('char', f.charFilter);
    if (f.obtainFilter) params.set('obtain', f.obtainFilter);
    if (f.supportFilter) params.set('support', f.supportFilter);
    if (f.rarity.length) params.set('rarity', f.rarity.join(','));
    if (f.trend.length) params.set('trend', f.trend.join(','));
    if (f.type.length) params.set('type', f.type.join(','));
    if (f.skill.length) params.set('skill', f.skill.join(','));
    if (f.favOnly) params.set('fav', '1');
    const qs = params.toString();
    history.replaceState(null, '', qs ? `?${qs}` : location.pathname);
}

function loadTlFromUrlParams() {
    const params = new URLSearchParams(location.search);
    if (!params.toString()) return false;

    const kw = params.get('q');
    if (kw) document.getElementById('tl-search-bar').value = kw;

    const mode = params.get('mode');
    if (mode === 'or') {
        const el = document.querySelector('input[name="tl-search-mode"][value="or"]');
        if (el) el.checked = true;
    }

    const charVal = params.get('char');
    if (charVal) document.getElementById('tl-char-filter').value = charVal;

    const obtainVal = params.get('obtain');
    if (obtainVal) document.getElementById('tl-obtain-filter').value = obtainVal;

    const supportVal = params.get('support');
    if (supportVal) document.getElementById('tl-support-filter').value = supportVal;

    (params.get('rarity') || '').split(',').filter(Boolean).forEach(v => {
        const el = document.querySelector(`.tl-rarity-filter[value="${v}"]`);
        if (el) el.checked = true;
    });
    (params.get('trend') || '').split(',').filter(Boolean).forEach(v => {
        const el = document.querySelector(`.tl-trend-filter[value="${v}"]`);
        if (el) el.checked = true;
    });
    (params.get('type') || '').split(',').filter(Boolean).forEach(v => {
        const el = document.querySelector(`.tl-type-filter[value="${v}"]`);
        if (el) el.checked = true;
    });
    (params.get('skill') || '').split(',').filter(Boolean).forEach(v => {
        const el = document.querySelector(`.tl-skill-filter[value="${v}"]`);
        if (el) el.checked = true;
    });

    if (params.get('fav') === '1') {
        const favEl = document.getElementById('tl-fav-only');
        if (favEl) favEl.checked = true;
    }
    return true;
}

// ==========================
// フィルタ適用
// ==========================
function buildTlFilters() {
    const rawKeyword = document.getElementById('tl-search-bar').value.trim().toLowerCase();
    return {
        keywords: rawKeyword ? rawKeyword.split(/\s+/) : [],
        searchMode: document.querySelector('input[name="tl-search-mode"]:checked').value,
        charFilter: document.getElementById('tl-char-filter').value,
        obtainFilter: document.getElementById('tl-obtain-filter').value,
        supportFilter: document.getElementById('tl-support-filter').value,
        rarity: Array.from(document.querySelectorAll('.tl-rarity-filter:checked')).map(cb => cb.value),
        trend: Array.from(document.querySelectorAll('.tl-trend-filter:checked')).map(cb => cb.value),
        type: Array.from(document.querySelectorAll('.tl-type-filter:checked')).map(cb => cb.value),
        skill: Array.from(document.querySelectorAll('.tl-skill-filter:checked')).map(cb => cb.value),
        favOnly: document.getElementById('tl-fav-only').checked,
    };
}

function cardMatches(card, f, favorites) {
    const d = card.dataset;

    if (f.charFilter && d.char !== f.charFilter) return false;
    if (f.obtainFilter && d.obtain !== f.obtainFilter) return false;
    if (f.supportFilter && d.support !== f.supportFilter) return false;
    if (f.rarity.length && !f.rarity.includes(d.rarity)) return false;
    if (f.trend.length && !f.trend.includes(d.trend)) return false;
    if (f.type.length && !f.type.includes(d.type)) return false;
    if (f.skill.length) {
        if (f.skill.includes('SP所持') && !d.skill.includes('SP')) return false;
        if (f.skill.includes('SP未所持') && d.skill.includes('SP')) return false;
        if (f.skill.includes('AA') && !d.skill.includes('AA')) return false;
    }
    if (favorites && !favorites.has(d.cardkey)) return false;

    if (f.keywords.length) {
        const text = `${d.char} ${d.card}`.toLowerCase();
        const hit = f.searchMode === 'and'
            ? f.keywords.every(kw => text.includes(kw))
            : f.keywords.some(kw => text.includes(kw));
        if (!hit) return false;
    }
    return true;
}

function applyTlFilters() {
    const f = buildTlFilters();
    const favorites = f.favOnly ? new Set(JSON.parse(localStorage.getItem('favorites') || '[]')) : null;
    const groups = document.querySelectorAll('.tl-group');
    let total = 0;

    groups.forEach(group => {
        const cards = group.querySelectorAll('.tl-card');
        let groupVisible = 0;
        cards.forEach(card => {
            const show = cardMatches(card, f, favorites);
            card.style.display = show ? '' : 'none';
            if (show) { groupVisible++; total++; }
        });
        group.style.display = groupVisible > 0 ? '' : 'none';
    });

    const cnt = document.getElementById('tl-count');
    if (cnt) cnt.textContent = total + '件';

    const statusEl = document.getElementById('filter-status');
    if (statusEl) {
        const isFiltering = f.keywords.length > 0 || !!f.charFilter || !!f.obtainFilter || !!f.supportFilter
            || f.rarity.length > 0 || f.trend.length > 0 || f.type.length > 0 || f.skill.length > 0 || !!f.favOnly;
        if (isFiltering) {
            document.getElementById('filter-status-text').textContent = `🔍 フィルタ中（${total}件表示）`;
        }
        statusEl.style.display = isFiltering ? '' : 'none';
    }

    localStorage.setItem('tlFilters', JSON.stringify(f));
    updateTlUrlParams(f);
}

function resetTlFilters() {
    document.getElementById('tl-search-bar').value = '';
    document.querySelector('input[name="tl-search-mode"][value="and"]').checked = true;
    document.getElementById('tl-char-filter').value = '';
    document.getElementById('tl-obtain-filter').value = '';
    document.getElementById('tl-support-filter').value = '';
    document.getElementById('tl-fav-only').checked = false;
    document.querySelectorAll('.tl-rarity-filter, .tl-trend-filter, .tl-type-filter, .tl-skill-filter')
        .forEach(cb => { cb.checked = false; });
    localStorage.removeItem('tlFilters');
    applyTlFilters();
}

function restoreTlFiltersFromStorage() {
    const saved = JSON.parse(localStorage.getItem('tlFilters') || 'null');
    if (!saved) return;
    document.getElementById('tl-search-bar').value = (saved.keywords || []).join(' ');
    if (saved.searchMode === 'or') {
        const el = document.querySelector('input[name="tl-search-mode"][value="or"]');
        if (el) el.checked = true;
    }
    if (saved.charFilter) document.getElementById('tl-char-filter').value = saved.charFilter;
    if (saved.obtainFilter) document.getElementById('tl-obtain-filter').value = saved.obtainFilter;
    if (saved.supportFilter) document.getElementById('tl-support-filter').value = saved.supportFilter;
    (saved.rarity || []).forEach(v => {
        const el = document.querySelector(`.tl-rarity-filter[value="${v}"]`);
        if (el) el.checked = true;
    });
    (saved.trend || []).forEach(v => {
        const el = document.querySelector(`.tl-trend-filter[value="${v}"]`);
        if (el) el.checked = true;
    });
    (saved.type || []).forEach(v => {
        const el = document.querySelector(`.tl-type-filter[value="${v}"]`);
        if (el) el.checked = true;
    });
    (saved.skill || []).forEach(v => {
        const el = document.querySelector(`.tl-skill-filter[value="${v}"]`);
        if (el) el.checked = true;
    });
    if (saved.favOnly) document.getElementById('tl-fav-only').checked = true;
}

// ==========================
// 画像として保存
// ==========================
function saveTimelineScreenshot() {
    const btn = document.getElementById('tl-screenshot-btn');
    const container = document.getElementById('tl-container');
    if (!container || typeof html2canvas === 'undefined') return;

    const originalLabel = btn.textContent;
    btn.disabled = true;
    btn.textContent = '画像を生成中...';

    html2canvas(container, { backgroundColor: '#f0f0f0', useCORS: true, scale: 2 }).then(canvas => {
        const link = document.createElement('a');
        link.download = 'release_timeline.png';
        link.href = canvas.toDataURL('image/png');
        link.click();
    }).catch(err => {
        console.error('スクリーンショットの生成に失敗しました', err);
        alert('画像の生成に失敗しました。');
    }).finally(() => {
        btn.disabled = false;
        btn.textContent = originalLabel;
    });
}

// ==========================
// 初期化
// ==========================
document.addEventListener('DOMContentLoaded', function() {
    if (window.innerWidth <= 768) {
        const filterBody = document.getElementById('tl-filter-body');
        if (filterBody) {
            filterBody.style.display = 'none';
            const icon = document.getElementById('tl-filter-toggle-icon');
            if (icon) icon.textContent = '▼';
        }
    }

    const loadedFromUrl = loadTlFromUrlParams();
    if (!loadedFromUrl) restoreTlFiltersFromStorage();

    document.getElementById('tl-search-bar').addEventListener('input', applyTlFilters);
    document.querySelectorAll('input[name="tl-search-mode"]').forEach(radio => {
        radio.addEventListener('change', applyTlFilters);
    });
    document.getElementById('tl-filter-body').addEventListener('change', applyTlFilters);
    document.getElementById('tl-screenshot-btn').addEventListener('click', saveTimelineScreenshot);

    window.addEventListener('scroll', function() {
        const btn = document.getElementById('scrollToTopBtn');
        if (btn) btn.style.display = window.scrollY > 200 ? 'block' : 'none';
    });

    applyTlFilters();
});
