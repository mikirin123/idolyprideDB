function buildFilters() {
    const rawKeyword = document.getElementById('search-bar').value.trim().toLowerCase();
    return {
        keywords:         rawKeyword ? rawKeyword.split(/\s+/) : [],
        searchMode:       document.querySelector('input[name="search-mode"]:checked').value,
        charFilter:       document.getElementById('filter-char').value,
        ctMin:            document.getElementById('ct-min').value !== '' ? parseInt(document.getElementById('ct-min').value, 10) : null,
        ctMax:            document.getElementById('ct-max').value !== '' ? parseInt(document.getElementById('ct-max').value, 10) : null,
        activeTrends:     new Set(Array.from(document.querySelectorAll('.trend-filter:checked')).map(cb => cb.value)),
        activeTypes:      new Set(Array.from(document.querySelectorAll('.type-filter:checked')).map(cb => cb.value)),
        activeSkillTypes: new Set(Array.from(document.querySelectorAll('.skilltype-filter:checked')).map(cb => cb.value)),
    };
}

function rowMatches(row, f) {
    const { char, skillType, ct, trend, type } = row.dataset;
    if (f.charFilter && char !== f.charFilter) return false;
    if (!f.activeTrends.has(trend)) return false;
    if (!f.activeTypes.has(type)) return false;
    if (!f.activeSkillTypes.has(skillType)) return false;
    if (f.ctMin !== null || f.ctMax !== null) {
        if (ct === '') return false;
        const ctVal = parseInt(ct, 10);
        if (f.ctMin !== null && ctVal < f.ctMin) return false;
        if (f.ctMax !== null && ctVal > f.ctMax) return false;
    }
    if (f.keywords.length) {
        const text = (row.querySelector('.skill-effect-cell')?.textContent || '').toLowerCase();
        const hit = f.searchMode === 'and'
            ? f.keywords.every(kw => text.includes(kw))
            : f.keywords.some(kw => text.includes(kw));
        if (!hit) return false;
    }
    return true;
}

function applyGroupedLayout(cardGroups) {
    // 既存のグループスタイルをリセット
    document.querySelectorAll('#skill-table tbody tr').forEach(r => r.classList.remove('card-group-first'));
    document.querySelectorAll('#skill-table .idol-cell').forEach(cell => {
        cell.removeAttribute('rowspan');
        cell.style.display = '';
    });
    // カードごとにアイドル列を縦結合
    cardGroups.forEach(groupRows => {
        groupRows[0].classList.add('card-group-first');
        groupRows[0].querySelector('.idol-cell').rowSpan = groupRows.length;
        groupRows.slice(1).forEach(r => {
            r.querySelector('.idol-cell').style.display = 'none';
        });
    });
}

function removeGroupedLayout() {
    document.querySelectorAll('#skill-table tbody tr').forEach(r => r.classList.remove('card-group-first'));
    document.querySelectorAll('#skill-table .idol-cell').forEach(cell => {
        cell.removeAttribute('rowspan');
        cell.style.display = '';
    });
}

function buildCardGroups(rows) {
    const map = new Map();
    rows.forEach(row => {
        const key = `${row.dataset.char}|||${row.dataset.card}`;
        if (!map.has(key)) map.set(key, []);
        map.get(key).push(row);
    });
    return map;
}

function applyFilters() {
    const f = buildFilters();
    const isGrouped = document.getElementById('mode-select').value === 'grouped';
    const rows = Array.from(document.querySelectorAll('#skill-table tbody tr'));
    let visibleCount = 0;

    if (isGrouped) {
        const cardGroups = buildCardGroups(rows);
        applyGroupedLayout(cardGroups);
        cardGroups.forEach(groupRows => {
            const show = groupRows.some(r => rowMatches(r, f));
            groupRows.forEach(r => {
                r.style.display = show ? '' : 'none';
                if (show) visibleCount++;
            });
        });
    } else {
        removeGroupedLayout();
        rows.forEach(row => {
            const show = rowMatches(row, f);
            row.style.display = show ? '' : 'none';
            if (show) visibleCount++;
        });
    }

    const total = rows.length;
    document.getElementById('result-count').textContent = visibleCount === total
        ? `全 ${total} 件`
        : `${visibleCount} / ${total} 件`;

    const statusEl = document.getElementById('filter-status');
    if (statusEl) {
        const isFiltering = f.keywords.length > 0 || !!f.charFilter || f.ctMin !== null || f.ctMax !== null
            || f.activeTrends.size < 3 || f.activeTypes.size < 3 || f.activeSkillTypes.size < 3;
        if (isFiltering) {
            document.getElementById('filter-status-text').textContent = `🔍 フィルタ中（${visibleCount}件表示）`;
        }
        statusEl.style.display = isFiltering ? '' : 'none';
    }

    saveSkillFiltersToStorage();
}

function saveSkillFiltersToStorage() {
    localStorage.setItem('skillFilters', JSON.stringify({
        keyword: document.getElementById('search-bar').value,
        searchMode: document.querySelector('input[name="search-mode"]:checked').value,
        mode: document.getElementById('mode-select').value,
        charFilter: document.getElementById('filter-char').value,
        ctMin: document.getElementById('ct-min').value,
        ctMax: document.getElementById('ct-max').value,
        trends: Array.from(document.querySelectorAll('.trend-filter:checked')).map(cb => cb.value),
        types: Array.from(document.querySelectorAll('.type-filter:checked')).map(cb => cb.value),
        skillTypes: Array.from(document.querySelectorAll('.skilltype-filter:checked')).map(cb => cb.value),
    }));
}

function restoreSkillFiltersFromStorage() {
    const saved = JSON.parse(localStorage.getItem('skillFilters') || 'null');
    if (!saved) return;
    document.getElementById('search-bar').value = saved.keyword || '';
    document.getElementById('mode-select').value = saved.mode || 'flat';
    document.getElementById('filter-char').value = saved.charFilter || '';
    document.getElementById('ct-min').value = saved.ctMin || '';
    document.getElementById('ct-max').value = saved.ctMax || '';
    if (saved.searchMode === 'or') {
        const el = document.querySelector('input[name="search-mode"][value="or"]');
        if (el) el.checked = true;
    }
    document.querySelectorAll('.trend-filter, .type-filter, .skilltype-filter').forEach(cb => { cb.checked = false; });
    (saved.trends || []).forEach(v => {
        const el = document.querySelector(`.trend-filter[value="${v}"]`);
        if (el) el.checked = true;
    });
    (saved.types || []).forEach(v => {
        const el = document.querySelector(`.type-filter[value="${v}"]`);
        if (el) el.checked = true;
    });
    (saved.skillTypes || []).forEach(v => {
        const el = document.querySelector(`.skilltype-filter[value="${v}"]`);
        if (el) el.checked = true;
    });
}

function resetFilters() {
    document.getElementById('search-bar').value = '';
    document.getElementById('mode-select').value = 'flat';
    document.getElementById('filter-char').value = '';
    document.getElementById('ct-min').value = '';
    document.getElementById('ct-max').value = '';
    document.querySelector('input[name="search-mode"][value="and"]').checked = true;
    document.querySelectorAll('.trend-filter, .type-filter, .skilltype-filter').forEach(cb => (cb.checked = true));
    localStorage.removeItem('skillFilters');
    applyFilters();
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('search-bar').addEventListener('input', applyFilters);
    document.getElementById('mode-select').addEventListener('change', applyFilters);
    document.getElementById('filter-char').addEventListener('change', applyFilters);
    document.getElementById('ct-min').addEventListener('input', applyFilters);
    document.getElementById('ct-max').addEventListener('input', applyFilters);
    document.querySelectorAll('input[name="search-mode"]').forEach(r => r.addEventListener('change', applyFilters));
    document.querySelectorAll('.trend-filter, .type-filter, .skilltype-filter').forEach(cb => cb.addEventListener('change', applyFilters));

    const scrollBtn = document.getElementById('scrollToTopBtn');
    window.addEventListener('scroll', () => {
        scrollBtn.style.display = document.documentElement.scrollTop > 100 ? 'block' : 'none';
    });
    scrollBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

    restoreSkillFiltersFromStorage();
    applyFilters();
});
