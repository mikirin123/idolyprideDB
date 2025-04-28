// ==========================
// キーワード検索機能
// ==========================
function performSearchAndFilter() {
    const keywordInput = document.getElementById('search-bar').value.trim().toLowerCase();
    const keywords = keywordInput.split(/\s+/); // スペースでキーワードを分割
    const searchMode = document.querySelector('input[name="search-mode"]:checked').value; // 検索モードを取得

    const form = document.getElementById('filter-form');
    const formData = new FormData(form);
    const filters = {
        character: formData.get('character'),
        rarity: formData.getAll('rarity'),
        obtain: formData.get('obtain'),
        trend: formData.getAll('trend'),
        type: formData.getAll('type'),
        skill: formData.getAll('skill'),
        support: formData.get('support')
    };

    const rows = Array.from(document.querySelectorAll('#character-table tr:not(:first-child)'));
    rows.forEach(row => {
        const cells = row.getElementsByTagName('td');
        const character = {
            character: cells[1].innerText,
            rarity: cells[3].innerText,
            obtain: cells[19].innerText,
            trend: cells[4].getAttribute("value"),
            type: cells[5].getAttribute("value"),
            skill: cells[6].innerText,
            support: cells[18].getAttribute("value"),
            card_name: cells[2]?.innerText || '',
            costume: cells[7]?.innerText || '',
            live_skill1_name: cells[12]?.innerText || '',
            live_skill1_effect: cells[13]?.innerText || '',
            live_skill2_name: cells[14]?.innerText || '',
            live_skill2_effect: cells[15]?.innerText || '',
            live_skill3_name: cells[16]?.innerText || '',
            live_skill3_effect: cells[17]?.innerText || ''
        };

        // 検索条件に基づく表示/非表示
        const matchesSearch = searchMode === 'and'
            ? keywords.every(keyword =>
                Object.values(character).some(value => value.toLowerCase().includes(keyword))
              )
            : keywords.some(keyword =>
                Object.values(character).some(value => value.toLowerCase().includes(keyword))
              );

        // フィルタ条件に基づく表示/非表示
        let matchesFilter = true;
        if (filters.character && filters.character !== character.character) matchesFilter = false;
        if (filters.rarity.length && !filters.rarity.includes(character.rarity)) matchesFilter = false;
        if (filters.obtain && filters.obtain !== character.obtain) matchesFilter = false;
        if (filters.trend.length && !filters.trend.includes(character.trend)) matchesFilter = false;
        if (filters.type.length && !filters.type.includes(character.type)) matchesFilter = false;
        if (filters.skill.length) {
            if (filters.skill.includes('SP所持') && !character.skill.includes('SP')) matchesFilter = false;
            if (filters.skill.includes('SP未所持') && character.skill.includes('SP')) matchesFilter = false;
            if (filters.skill.includes('AA') && !character.skill.includes('AA')) matchesFilter = false;
        }
        if (filters.support && filters.support !== character.support) matchesFilter = false;

        // 両方の条件を満たす場合のみ表示
        row.style.display = matchesSearch && matchesFilter ? '' : 'none';
    });
}

// ==========================
// イベントリスナーの修正
// ==========================
document.getElementById('search-button').addEventListener('click', performSearchAndFilter);
document.querySelectorAll('input[name="search-mode"]').forEach(radio => {
    radio.addEventListener('change', performSearchAndFilter);
});
document.getElementById('filter-form').addEventListener('change', performSearchAndFilter);

// ==========================
// フィルタリセット機能
// ==========================
function resetFilters() {
    document.getElementById('filter-form').reset();
    document.getElementById('search-bar').value = '';
    const rows = Array.from(document.querySelectorAll('#character-table tr:not(:first-child)'));
    rows.forEach(row => row.style.display = '');

    // ID順に並び替え
    rows.sort((a, b) => {
        const aId = parseInt(a.getElementsByTagName('td')[0].innerText);
        const bId = parseInt(b.getElementsByTagName('td')[0].innerText);
        return aId - bId;
    });

    const table = document.getElementById('character-table');
    rows.forEach(row => table.appendChild(row));

    // localStorageのフィルタ状態をクリア
    localStorage.clear();
}

// ==========================
// スクロールトップボタンの表示制御
// ==========================
window.onscroll = function() {
    const scrollToTopBtn = document.getElementById('scrollToTopBtn');
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        if (window.innerWidth > 768) {
            scrollToTopBtn.style.display = "block";
        }
    } else {
        scrollToTopBtn.style.display = "none";
    }
};

// ==========================
// スクロールトップボタンのクリックイベント
// ==========================
document.getElementById('scrollToTopBtn').addEventListener('click', function() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
});

// ==========================
// ページ読み込み時の初期化処理
// ==========================
document.addEventListener('DOMContentLoaded', function() {
    // スクロールトップボタンの初期化
    const scrollToTopBtn = document.getElementById('scrollToTopBtn');
    if (scrollToTopBtn) {
        scrollToTopBtn.style.display = "none"; // 初期状態では非表示
    } else {
        console.error('スクロールトップボタンが見つかりません');
    }


    // ヒントアイコンの設定
    const hintIcons = document.querySelectorAll('.hint-icon');
    const hintPopups = document.querySelectorAll('.hint-popup');
    hintIcons.forEach((hintIcon, index) => {
        const hintPopup = hintPopups[index];
        hintIcon.addEventListener('click', function(event) {
            event.stopPropagation();
            hintPopup.style.display = hintPopup.style.display === 'block' ? 'none' : 'block';
        });
    });

    window.addEventListener('click', function(event) {
        hintPopups.forEach(hintPopup => {
            if (!hintPopup.contains(event.target)) {
                hintPopup.style.display = 'none';
            }
        });
    });

    const bannerTitle = document.querySelector('.banner_title');
    bannerTitle.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // 検索バーの設定
    const searchBar = document.getElementById('search-bar');
    if (searchBar) {
        searchBar.addEventListener('input', function() {
            performSearchAndFilter();
        });
    } else {
        console.error('検索バーが見つかりません');
    }

    // localStorageから「全て表示する」状態を復元
    const showAll = localStorage.getItem('showAll') === 'true';
    if (showAll) {
        const showAllButton = document.getElementById('show-all-btn');
        showAllButton.click(); // 「全て表示する」ボタンをクリック
    }

    // localStorageからフィルタ状態を復元
    const savedFilters = JSON.parse(localStorage.getItem('filters'));
    const savedSortOrder = localStorage.getItem('sortOrder');
    const savedKeyword = localStorage.getItem('keyword');

    if (savedFilters) {
        const form = document.getElementById('filter-form');
        const formData = new FormData(form);

        // フィルタフォームに復元
        Object.keys(savedFilters).forEach(key => {
            if (Array.isArray(savedFilters[key])) {
                savedFilters[key].forEach(value => {
                    const input = form.querySelector(`[name="${key}"][value="${value}"]`);
                    if (input) input.checked = true;
                });
            } else {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) input.value = savedFilters[key];
            }
        });

        // 並び順を復元
        if (savedSortOrder) {
            const sortOrderInput = form.querySelector(`[name="sort-order"][value="${savedSortOrder}"]`);
            if (sortOrderInput) sortOrderInput.checked = true;
        }

        // 検索キーワードを復元
        if (savedKeyword) {
            document.getElementById('search-bar').value = savedKeyword;
        }

        // フィルタを適用
        applyFilters();
    }
});

function scrollWithOffset(event) {
    event.preventDefault(); // 通常のジャンプを止める
    const href = event.currentTarget.getAttribute("href");
    const target = document.querySelector(href);
    if (target) {
      const offset = 70; // ← ここでずらす量を調整
      const position = target.getBoundingClientRect().top + window.pageYOffset - offset;
      window.scrollTo({ top: position, behavior: 'smooth' });
    }
  }
