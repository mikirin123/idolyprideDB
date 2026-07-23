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

    // イベントの終了日時が指定の期限区分に該当するか判定する(「◯日以内」は累積)
    function matchesDeadline(endDt, deadline) {
        if (!deadline) return true;
        if (deadline === 'today') return endDt <= jstMidnightBoundary(1);
        if (deadline === '3days') return endDt <= jstMidnightBoundary(3);
        if (deadline === '7days') return endDt <= jstMidnightBoundary(7);
        if (deadline === 'later') return endDt > jstMidnightBoundary(7);
        return true;
    }

    function applyFilters() {
        const activeCats = catCheckboxes.filter(cb => cb.checked).map(cb => cb.value);
        const deadline = deadlineSelect.value;
        let visibleCount = 0;

        items.forEach(item => {
            const endDt = new Date(item.dataset.end);
            let show = true;
            if (activeCats.length && !activeCats.includes(item.dataset.category)) show = false;
            if (!matchesDeadline(endDt, deadline)) show = false;
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
