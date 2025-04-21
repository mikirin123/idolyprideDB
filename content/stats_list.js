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

        // ソート順を示す三角を更新
        document.querySelectorAll('th.sortable').forEach(th => th.classList.remove('sorted', 'sorted-asc'));
        th.classList.add('sorted');
        if (isSameColumn && !isAscending) {
            th.classList.add('sorted-asc');
        }
    })));
});
