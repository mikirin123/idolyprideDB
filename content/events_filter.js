document.addEventListener('DOMContentLoaded', function() {
    const items = Array.from(document.querySelectorAll('.event-item:not(.event-empty)'));
    if (!items.length) return;

    const catCheckboxes = Array.from(document.querySelectorAll('.event-cat-filter'));
    const deadlineSelect = document.getElementById('event-deadline-filter');
    const resetBtn = document.getElementById('event-filter-reset');
    const emptyMsg = document.getElementById('event-empty-filtered');

    const JST_OFFSET_MS = 9 * 60 * 60 * 1000;

    // 現在時刻(JST)から daysAhead 日後の 0:00(JST)の Date を返す
    function jstMidnightBoundary(daysAhead) {
        const nowJst = new Date(Date.now() + JST_OFFSET_MS);
        const boundaryUtcMs = Date.UTC(nowJst.getUTCFullYear(), nowJst.getUTCMonth(), nowJst.getUTCDate() + daysAhead);
        return new Date(boundaryUtcMs - JST_OFFSET_MS);
    }

    // イベントの終了日時が暦日(JST)でどの期限区分に収まるかを判定する
    function deadlineBucket(endDt) {
        if (endDt <= jstMidnightBoundary(1)) return 'today';
        if (endDt <= jstMidnightBoundary(3)) return '3days';
        if (endDt <= jstMidnightBoundary(7)) return '7days';
        return 'later';
    }

    function applyFilters() {
        const activeCats = catCheckboxes.filter(cb => cb.checked).map(cb => cb.value);
        const deadline = deadlineSelect.value;
        let visibleCount = 0;

        items.forEach(item => {
            const endDt = new Date(item.dataset.end);
            let show = true;
            if (activeCats.length && !activeCats.includes(item.dataset.category)) show = false;
            if (deadline && deadlineBucket(endDt) !== deadline) show = false;
            item.style.display = show ? '' : 'none';
            if (show) visibleCount++;
        });

        emptyMsg.style.display = visibleCount === 0 ? 'block' : 'none';
    }

    catCheckboxes.forEach(cb => cb.addEventListener('change', applyFilters));
    deadlineSelect.addEventListener('change', applyFilters);
    resetBtn.addEventListener('click', function() {
        catCheckboxes.forEach(cb => { cb.checked = false; });
        deadlineSelect.value = '';
        applyFilters();
    });
});
