function applyStatsFilter() {
    const char = document.getElementById('f-char')?.value || '';
    const trend = document.getElementById('f-trend')?.value || '';
    const type = document.getElementById('f-type')?.value || '';
    const obtain = document.getElementById('f-obtain')?.value || '';
    const rows = document.querySelectorAll('.stats_list-table tr:not(:first-child)');
    let visible = 0;
    rows.forEach(function(row) {
        const show = (!char || row.dataset.char === char)
            && (!trend || row.dataset.trend === trend)
            && (!type || row.dataset.type === type)
            && (!obtain || row.dataset.obtain === obtain);
        row.style.display = show ? '' : 'none';
        if (show) visible++;
    });
    const cnt = document.getElementById('stats-filter-count');
    if (cnt) cnt.textContent = visible + '件';

    const statusEl = document.getElementById('filter-status');
    if (statusEl) {
        const isFiltering = !!char || !!trend || !!type || !!obtain;
        if (isFiltering) {
            document.getElementById('filter-status-text').textContent = `🔍 フィルタ中（${visible}件表示）`;
        }
        statusEl.style.display = isFiltering ? '' : 'none';
    }

    localStorage.setItem('statsFilters', JSON.stringify({ char, trend, type, obtain }));
}

function resetStatsFilter() {
    ['f-char','f-trend','f-type','f-obtain'].forEach(function(id) {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
    localStorage.removeItem('statsFilters');
    applyStatsFilter();
}

function restoreStatsFiltersFromStorage() {
    const saved = JSON.parse(localStorage.getItem('statsFilters') || 'null');
    if (!saved) return;
    const idMap = { char: 'f-char', trend: 'f-trend', type: 'f-type', obtain: 'f-obtain' };
    Object.entries(idMap).forEach(([key, id]) => {
        const el = document.getElementById(id);
        if (el && saved[key]) el.value = saved[key];
    });
}

document.addEventListener('DOMContentLoaded', function() {
    ['f-char','f-trend','f-type','f-obtain'].forEach(function(id) {
        const el = document.getElementById(id);
        if (el) el.addEventListener('change', applyStatsFilter);
    });
    restoreStatsFiltersFromStorage();
    applyStatsFilter();
    const bannerTitle = document.querySelector('.banner_title');
    bannerTitle.addEventListener('click', function() {
        location.href = '../index.html';
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

    const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;

    const comparer = (idx, asc) => (a, b) => ((v1, v2) =>
        v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)
    )(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

    document.querySelectorAll('th.sortable').forEach(th => th.addEventListener('click', (() => {
        const table = th.closest('table');
        const idx = Array.from(th.parentNode.children).indexOf(th); // インデックスを修正
        const isSameColumn = th.classList.contains('sorted');
        const isAscending = th.classList.contains('sorted-asc');
        document.querySelectorAll('th.sortable').forEach(th => th.classList.remove('sorted', 'sorted-asc'));
        th.classList.add('sorted');
        if (isSameColumn && !isAscending) {
            th.classList.add('sorted-asc');
        }
        Array.from(table.querySelectorAll('tr:nth-child(n+2)'))
            .sort(comparer(idx, this.asc = isSameColumn ? !this.asc : false)) // 他のカラムをクリックしたときに降順から始める
            .forEach(tr => table.appendChild(tr));
    })));
});
