document.addEventListener('DOMContentLoaded', function() {
    const items = Array.from(document.querySelectorAll('.event-item:not(.event-empty)'));
    if (!items.length) return;

    const catCheckboxes = Array.from(document.querySelectorAll('.event-cat-filter'));
    const deadlineSelect = document.getElementById('event-deadline-filter');
    const resetBtn = document.getElementById('event-filter-reset');
    const emptyMsg = document.getElementById('event-empty-filtered');

    const DAY_MS = 24 * 60 * 60 * 1000;

    // イベントの終了日時までの残り時間から期限区分を判定する
    function deadlineBucket(endDt) {
        const diff = endDt - new Date();
        if (diff <= DAY_MS) return 'today';
        if (diff <= 3 * DAY_MS) return '3days';
        if (diff <= 7 * DAY_MS) return '7days';
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
