// ==========================
// フィルターURL同期
// ==========================
function updateUrlParams() {
    const form = document.getElementById('filter-form');
    if (!form) return;
    const formData = new FormData(form);
    const params = new URLSearchParams();
    const kw = document.getElementById('search-bar')?.value.trim();
    if (kw) params.set('q', kw);
    const searchMode = document.querySelector('input[name="search-mode"]:checked')?.value;
    if (searchMode && searchMode !== 'and') params.set('mode', searchMode);
    if (formData.get('character')) params.set('char', formData.get('character'));
    if (formData.get('obtain')) params.set('obtain', formData.get('obtain'));
    if (formData.get('support')) params.set('support', formData.get('support'));
    const rarity = formData.getAll('rarity');
    if (rarity.length) params.set('rarity', rarity.join(','));
    const trend = formData.getAll('trend');
    if (trend.length) params.set('trend', trend.join(','));
    const type = formData.getAll('type');
    if (type.length) params.set('type', type.join(','));
    const skill = formData.getAll('skill');
    if (skill.length) params.set('skill', skill.join(','));
    const sort = formData.get('sort');
    if (sort && sort !== 'id') params.set('sort', sort);
    const sortorder = document.querySelector('input[name="sort-order"]:checked')?.value;
    if (sortorder && sortorder !== 'desc') params.set('sortorder', sortorder);
    if (document.getElementById('fav-only')?.checked) params.set('fav', '1');
    const qs = params.toString();
    history.replaceState(null, '', qs ? `?${qs}` : location.pathname);
}

function loadFromUrlParams() {
    const params = new URLSearchParams(location.search);
    if (!params.toString()) return false;
    const form = document.getElementById('filter-form');
    if (!form) return false;

    const kw = params.get('q');
    if (kw) document.getElementById('search-bar').value = kw;

    if (params.get('mode') === 'or') {
        const orRadio = document.querySelector('input[name="search-mode"][value="or"]');
        if (orRadio) orRadio.checked = true;
    }

    const charVal = params.get('char');
    if (charVal) { const el = form.querySelector('[name="character"]'); if (el) el.value = charVal; }

    const obtainVal = params.get('obtain');
    if (obtainVal) { const el = form.querySelector('[name="obtain"]'); if (el) el.value = obtainVal; }

    const supportVal = params.get('support');
    if (supportVal) { const el = form.querySelector('[name="support"]'); if (el) el.value = supportVal; }

    (params.get('rarity') || '').split(',').filter(Boolean).forEach(v => {
        const el = form.querySelector(`[name="rarity"][value="${v}"]`);
        if (el) el.checked = true;
    });
    (params.get('trend') || '').split(',').filter(Boolean).forEach(v => {
        const el = form.querySelector(`[name="trend"][value="${v}"]`);
        if (el) el.checked = true;
    });
    (params.get('type') || '').split(',').filter(Boolean).forEach(v => {
        const el = form.querySelector(`[name="type"][value="${v}"]`);
        if (el) el.checked = true;
    });
    (params.get('skill') || '').split(',').filter(Boolean).forEach(v => {
        const el = form.querySelector(`[name="skill"][value="${v}"]`);
        if (el) el.checked = true;
    });

    const sortVal = params.get('sort') || 'id';
    const sortEl = form.querySelector(`[name="sort"][value="${sortVal}"]`);
    if (sortEl) sortEl.checked = true;

    const sortorderVal = params.get('sortorder') || 'desc';
    const sortorderEl = form.querySelector(`[name="sort-order"][value="${sortorderVal}"]`);
    if (sortorderEl) sortorderEl.checked = true;

    if (params.get('fav') === '1') {
        const favEl = document.getElementById('fav-only');
        if (favEl) favEl.checked = true;
    }
    return true;
}

// ==========================
// フィルターアコーディオン
// ==========================
function toggleFilter() {
    const body = document.getElementById('filter-body');
    const icon = document.getElementById('filter-toggle-icon');
    const isOpen = body.style.display !== 'none';
    body.style.display = isOpen ? 'none' : '';
    icon.textContent = isOpen ? '▼' : '▲';
}

// ==========================
// ページネーション
// ==========================
let currentPage = 1;
const PAGE_SIZE = 50;

function applyPagination() {
    const table = document.getElementById('character-table');
    const allRows = Array.from(table.querySelectorAll('tr:not(:first-child)'));
    const filtered = allRows.filter(r => r.dataset.visible !== '0');

    const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
    if (currentPage > totalPages) currentPage = totalPages;

    const start = (currentPage - 1) * PAGE_SIZE;
    const end = start + PAGE_SIZE;

    filtered.forEach((row, idx) => {
        row.style.display = (idx >= start && idx < end) ? '' : 'none';
    });
    allRows.filter(r => r.dataset.visible === '0').forEach(r => { r.style.display = 'none'; });

    renderPagination(totalPages, filtered.length);
}

function renderPagination(totalPages, totalCount) {
    let pg = document.getElementById('pagination');
    if (!pg) {
        pg = document.createElement('div');
        pg.id = 'pagination';
        const table = document.getElementById('character-table');
        table.parentNode.insertBefore(pg, table.nextSibling);
    }
    if (totalPages <= 1) {
        pg.innerHTML = `<span class="pg-count">${totalCount}件</span>`;
        return;
    }
    let html = `<span class="pg-count">${totalCount}件</span>`;
    html += `<button onclick="goPage(1)" ${currentPage === 1 ? 'disabled' : ''}>«</button>`;
    html += `<button onclick="goPage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>‹</button>`;
    for (let p = Math.max(1, currentPage - 2); p <= Math.min(totalPages, currentPage + 2); p++) {
        html += `<button onclick="goPage(${p})" class="${p === currentPage ? 'pg-active' : ''}">${p}</button>`;
    }
    html += `<button onclick="goPage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>›</button>`;
    html += `<button onclick="goPage(${totalPages})" ${currentPage === totalPages ? 'disabled' : ''}>»</button>`;
    html += `<span class="pg-info">${currentPage}/${totalPages}ページ</span>`;
    pg.innerHTML = html;
}

function goPage(p) {
    currentPage = p;
    applyPagination();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ==========================
// 並び替え機能
// ==========================
function sortTable() {
    const sortKey = document.querySelector('input[name="sort"]:checked').value;
    const sortOrder = document.querySelector('input[name="sort-order"]:checked').value;
    const table = document.getElementById('character-table');
    const rows = Array.from(table.querySelectorAll('tr:not(:first-child)'));

    // カラムインデックスの対応（先頭に★列があるため+1ずれ）
    const colIndexMap = {
        id: 2,
        "ボーカル": 11,
        "ダンス": 12,
        "ビジュアル": 13,
        "スタミナ": 14
    };
    const colIndex = colIndexMap[sortKey] ?? 0;

    rows.sort((a, b) => {
        let aVal = a.getElementsByTagName('td')[colIndex].innerText;
        let bVal = b.getElementsByTagName('td')[colIndex].innerText;
        // 数値比較
        if (["id", "ボーカル", "ダンス", "ビジュアル", "スタミナ"].includes(sortKey)) {
            aVal = parseInt(aVal) || 0;
            bVal = parseInt(bVal) || 0;
        }
        if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1;
        return 0;
    });

    rows.forEach(row => table.appendChild(row));
}

// 並び替えラジオボタンのイベントリスナー
document.querySelectorAll('input[name="sort"], input[name="sort-order"]').forEach(input => {
    input.addEventListener('change', function() {
        currentPage = 1;
        sortTable();
        applyPagination();
    });
});

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

    const favOnly = document.getElementById('fav-only')?.checked;
    const favorites = favOnly ? new Set(JSON.parse(localStorage.getItem('favorites') || '[]')) : null;

    const rows = Array.from(document.querySelectorAll('#character-table tr:not(:first-child)'));
    rows.forEach(row => {
        const cells = row.getElementsByTagName('td');
        const character = {
            character: cells[3].innerText,
            rarity: cells[5].innerText,
            obtain: cells[24].innerText,
            trend: cells[6].getAttribute("value"),
            type: cells[7].getAttribute("value"),
            skill: cells[8].innerText,
            support: cells[23].getAttribute("value"),
            card_name: cells[4]?.innerText || '',
            costume: cells[9]?.innerText || '',
            live_skill1_name: cells[15]?.innerText || '',
            live_skill1_effect: cells[16]?.innerText || '',
            live_skill2_name: cells[17]?.innerText || '',
            live_skill2_effect: cells[18]?.innerText || '',
            live_skill3_name: cells[19]?.innerText || '',
            live_skill3_effect: cells[20]?.innerText || ''
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

        if (favorites && !favorites.has(row.dataset.cardkey)) matchesFilter = false;

        // 両方の条件を満たす場合のみ表示
        const matches = matchesSearch && matchesFilter;
        row.dataset.visible = matches ? '1' : '0';
        row.style.display = matches ? '' : 'none';
    });
    // 検索・フィルタ後にも並び替えを適用
    sortTable();
    currentPage = 1;
    applyPagination();

    updateFilterStatus(keywordInput, filters, favOnly, rows);

    // フィルター状態を保存
    localStorage.setItem('filters', JSON.stringify(filters));
    localStorage.setItem('keyword', document.getElementById('search-bar').value);
    const sortOrder = document.querySelector('input[name="sort-order"]:checked');
    if (sortOrder) localStorage.setItem('sortOrder', sortOrder.value);

    updateUrlParams();
}

// ==========================
// フィルタ中インジケーター
// ==========================
function updateFilterStatus(keyword, filters, favOnly, rows) {
    const statusEl = document.getElementById('filter-status');
    if (!statusEl) return;

    const isFiltering = !!keyword || !!filters.character || !!filters.obtain || !!filters.support
        || filters.rarity.length > 0 || filters.trend.length > 0 || filters.type.length > 0 || filters.skill.length > 0
        || !!favOnly;

    if (!isFiltering) {
        statusEl.style.display = 'none';
        return;
    }

    const visibleCount = rows.filter(r => r.dataset.visible === '1').length;
    document.getElementById('filter-status-text').textContent = `フィルタ中（${visibleCount}件表示）`;
    statusEl.style.display = '';
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
    // search-mode ラジオは #filter-form の外にあるため reset() の対象外
    const andRadio = document.querySelector('input[name="search-mode"][value="and"]');
    if (andRadio) andRadio.checked = true;
    ['filters', 'sortOrder', 'keyword', 'showAll'].forEach(k => localStorage.removeItem(k));
    performSearchAndFilter();
}

// ==========================
// スクロールトップボタンの表示制御
// ==========================
window.onscroll = function() {
    const scrollToTopBtn = document.getElementById('scrollToTopBtn');
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        scrollToTopBtn.style.display = "block";
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
// 画像キャッシュの確認と適用
// ==========================
function optimizeImageLoading() {
    const images = document.querySelectorAll('img[loading="lazy"]');
    images.forEach(img => {
        if (img.complete && img.naturalHeight !== 0) {
            img.classList.add('cached'); // キャッシュ済みの場合は即座に表示
        } else {
            img.addEventListener('load', () => {
                img.style.opacity = '1'; // 遅延ロード後に表示
            });
        }
    });
}

// ==========================
// ページ読み込み時の初期化処理
// ==========================
document.addEventListener('DOMContentLoaded', function() {
    // スマホ時はフィルターをデフォルトで閉じる
    if (window.innerWidth <= 768) {
        const filterBody = document.getElementById('filter-body');
        if (filterBody) {
            filterBody.style.display = 'none';
            const icon = document.getElementById('filter-toggle-icon');
            if (icon) icon.textContent = '▼';
        }
    }

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
        location.href = '../index.html';
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

    // お気に入りの初期化
    initFavorites();
    document.querySelectorAll('.fav-btn').forEach(btn => {
        btn.addEventListener('click', () => toggleFavorite(btn));
    });
    document.getElementById('fav-only')?.addEventListener('change', performSearchAndFilter);

    // デフォルトで実装順降順に並び替え
    document.getElementById('sort-id').checked = true;
    document.querySelector('input[name="sort-order"][value="desc"]').checked = true;
    sortTable();

    // URLパラメータ → localStorageの順で優先復元
    const loadedFromUrl = loadFromUrlParams();

    if (!loadedFromUrl) {
        // localStorageからフィルタ状態を復元
        const savedFilters = JSON.parse(localStorage.getItem('filters'));
        const savedSortOrder = localStorage.getItem('sortOrder');
        const savedKeyword = localStorage.getItem('keyword');

        if (savedFilters) {
            const form = document.getElementById('filter-form');

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

            if (savedSortOrder) {
                const sortOrderInput = form.querySelector(`[name="sort-order"][value="${savedSortOrder}"]`);
                if (sortOrderInput) sortOrderInput.checked = true;
            }

            if (savedKeyword) {
                document.getElementById('search-bar').value = savedKeyword;
            }
        }
    }

    // 常にフィルタ適用（初期表示含む）
    performSearchAndFilter();

});

// ==========================
// お気に入り機能
// ==========================
function toggleFavorite(btn) {
    const key = btn.dataset.key;
    let favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    if (favorites.includes(key)) {
        favorites = favorites.filter(k => k !== key);
        btn.textContent = '☆';
        btn.classList.remove('fav-active');
    } else {
        favorites.push(key);
        btn.textContent = '★';
        btn.classList.add('fav-active');
    }
    localStorage.setItem('favorites', JSON.stringify(favorites));
}

function initFavorites() {
    const favorites = new Set(JSON.parse(localStorage.getItem('favorites') || '[]'));
    document.querySelectorAll('.fav-btn').forEach(btn => {
        if (favorites.has(btn.dataset.key)) {
            btn.textContent = '★';
            btn.classList.add('fav-active');
        }
    });
}

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
