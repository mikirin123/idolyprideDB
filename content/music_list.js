function buildFilters() {
    const rawKeyword = document.getElementById('search-bar').value.trim().toLowerCase();
    return {
        keywords:   rawKeyword ? rawKeyword.split(/\s+/) : [],
        groupFilter: document.getElementById('filter-group').value,
        memberFilter: document.getElementById('filter-member').value,
    };
}

function rowMatches(row, f) {
    const { group, members } = row.dataset;
    const memberList = members ? members.split('|') : [];
    if (f.groupFilter && group !== f.groupFilter) return false;
    if (f.memberFilter && !memberList.includes(f.memberFilter)) return false;
    if (f.keywords.length) {
        const text = row.textContent.toLowerCase();
        if (!f.keywords.every(kw => text.includes(kw))) return false;
    }
    return true;
}

function applyFilters() {
    const f = buildFilters();
    const rows = Array.from(document.querySelectorAll('#music-table tbody tr'));
    let visibleCount = 0;

    rows.forEach(row => {
        const show = rowMatches(row, f);
        row.style.display = show ? '' : 'none';
        if (show) visibleCount++;
    });

    const total = rows.length;
    document.getElementById('result-count').textContent = visibleCount === total
        ? `全 ${total} 件`
        : `${visibleCount} / ${total} 件`;
}

function resetFilters() {
    document.getElementById('search-bar').value = '';
    document.getElementById('filter-group').value = '';
    document.getElementById('filter-member').value = '';
    applyFilters();
}

document.addEventListener('DOMContentLoaded', () => {
    let searchDebounceTimer;
    document.getElementById('search-bar').addEventListener('input', function() {
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(applyFilters, 150);
    });
    document.getElementById('filter-group').addEventListener('change', applyFilters);
    document.getElementById('filter-member').addEventListener('change', applyFilters);

    const scrollBtn = document.getElementById('scrollToTopBtn');
    window.addEventListener('scroll', () => {
        scrollBtn.style.display = document.documentElement.scrollTop > 100 ? 'block' : 'none';
    });
    scrollBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

    applyFilters();
});
