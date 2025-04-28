// ==========================
// フィルタ適用機能
// ==========================
function applyFilters() {
    // フィルタフォームのデータを取得
    const form = document.getElementById('filter-form');
    const formData = new FormData(form);
    const filters = {
        character: formData.get('character'),
        rarity: formData.getAll('rarity'),
        obtain: formData.get('obtain'),
        trend: formData.getAll('trend'),
        type: formData.getAll('type'),
        skill: formData.getAll('skill'),
        support: formData.get('support'),
        sort: formData.get('sort')
    };
    const sortOrder = formData.get('sort-order') || 'asc';
    const keyword = document.getElementById('search-bar').value.toLowerCase();

    // テーブルの行をフィルタリング
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
            vocal: parseInt(cells[8].innerText),
            dance: parseInt(cells[9].innerText),
            visual: parseInt(cells[10].innerText),
            stamina: parseInt(cells[11].innerText),
            card_name: cells[2].innerText,
            costume: cells[7].innerText,
            live_skill1_name: cells[12].innerText,
            live_skill1_effect: cells[13].innerText,
            live_skill2_name: cells[14].innerText,
            live_skill2_effect: cells[15].innerText,
            live_skill3_name: cells[16].innerText,
            live_skill3_effect: cells[17].innerText
        };

        // フィルタ条件に基づいて表示/非表示を切り替え
        let show = true;
        if (filters.character && filters.character !== character.character) show = false;
        if (filters.rarity.length && !filters.rarity.includes(character.rarity)) show = false;
        if (filters.obtain && filters.obtain !== character.obtain) show = false;
        if (filters.trend.length && !filters.trend.includes(character.trend)) show = false;
        if (filters.type.length && !filters.type.includes(character.type)) show = false;
        if (filters.skill.length) {
            if (filters.skill.includes('SP所持') && !character.skill.includes('SP')) show = false;
            if (filters.skill.includes('SP未所持') && character.skill.includes('SP')) show = false;
            if (filters.skill.includes('AA') && !character.skill.includes('AA')) show = false;
        }
        if (filters.support && filters.support !== character.support) show = false;
        if (keyword && !(
            character.card_name.toLowerCase().includes(keyword) ||
            character.costume.toLowerCase().includes(keyword) ||
            character.live_skill1_name.toLowerCase().includes(keyword) ||
            character.live_skill1_effect.toLowerCase().includes(keyword) ||
            character.live_skill2_name.toLowerCase().includes(keyword) ||
            character.live_skill2_effect.toLowerCase().includes(keyword) ||
            character.live_skill3_name.toLowerCase().includes(keyword) ||
            character.live_skill3_effect.toLowerCase().includes(keyword)
        )) {
            show = false;
        }

        row.style.display = show ? '' : 'none';
    });

    // 並び替え処理
    if (filters.sort) {
        rows.sort((a, b) => {
            const aCells = a.getElementsByTagName('td');
            const bCells = b.getElementsByTagName('td');
            let comparison = 0;
            if (filters.sort === 'id') {
                const aId = parseInt(aCells[0].innerText);
                const bId = parseInt(bCells[0].innerText);
                comparison = aId - bId;
            } else {
                const aValue = parseInt(aCells[filters.sort === 'ボーカル' ? 8 : filters.sort === 'ダンス' ? 9 : filters.sort === 'ビジュアル' ? 10 : 11].innerText);
                const bValue = parseInt(bCells[filters.sort === 'ボーカル' ? 8 : filters.sort === 'ダンス' ? 9 : filters.sort === 'ビジュアル' ? 10 : 11].innerText);
                comparison = aValue - bValue;
            }
            return sortOrder === 'asc' ? comparison : -comparison;
        });

        const table = document.getElementById('character-table');
        rows.forEach(row => table.appendChild(row));
    }

    // フィルタ状態をlocalStorageに保存
    localStorage.setItem('filters', JSON.stringify(filters));
    localStorage.setItem('sortOrder', sortOrder);
    localStorage.setItem('keyword', keyword);
}

// ==========================
// フィルタリセット機能
// ==========================
function resetFilters() {
    const form = document.getElementById('filter-form');
    form.reset();
    document.getElementById('search-bar').value = '';
    const rows = Array.from(document.querySelectorAll('#character-table tr:not(:first-child)'));
    rows.forEach(row => {
        row.style.display = '';
    });

    // ID順に並び替え
    rows.sort((a, b) => {
        const aId = parseInt(a.getElementsByTagName('td')[0].innerText);
        const bId = parseInt(b.getElementsByTagName('td')[0].innerText);
        return aId - bId;
    });

    const table = document.getElementById('character-table');
    rows.forEach(row => table.appendChild(row));

    // localStorageのフィルタ状態をクリア
    localStorage.removeItem('filters');
    localStorage.removeItem('sortOrder');
    localStorage.removeItem('keyword');
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
    // メニューの設定
    const menu = document.querySelector('.menu');
    menu.tagName = 'button'; // タグをbuttonに変更
    menu.style.position = 'absolute';
    menu.style.right = '60px';
    menu.style.top = '50%';
    menu.style.transform = 'translateY(-50%)';
    const menuContent = document.querySelector('.menu-content');
    const popup = document.querySelector('.popup');
    const popupHeader = document.querySelector('.popup-header');
    const popupContent = document.querySelector('.popup-content');
    const popupClose = document.querySelector('.popup-close');

    menu.addEventListener('click', function() {
        menuContent.style.display = menuContent.style.display === 'block' ? 'none' : 'block';
    });

    window.addEventListener('click', function(event) {
        if (!menu.contains(event.target)) {
            menuContent.style.display = 'none';
        }
    });

    document.querySelectorAll('.menu-content a').forEach(item => {
        item.addEventListener('click', function() {
            const menuName = this.innerText;
            popupHeader.innerText = menuName; // ポップアップのヘッダーにタイトルを設定
            if (menuName === '') {
                popupContent.innerHTML = '';
                popup.style.display = 'block';
                popupOverlay.style.display = 'block';
            } else if (menuName === ' このサイトについて') {
                popupContent.innerHTML = '● 作成者<br>miki<br><br>● 推薦環境<br>chrome(最新版)<br>Safari (Mac・iOS最新版)<br>Firefox (最新版)<br><br>改善要望・不具合報告は<br><a href="https://x.com/miki_aipr" class="about_link">twitter</a>または<a href="https://forms.gle/gM8HjG6Hzq4YxCmh9" class="about_link">Googleフォーム</a>までお願いします。';
                popup.style.display = 'block';
                popupOverlay.style.display = 'block';
            } 
        });
    });

    // ポップアップの設定
    const popupOverlay = document.createElement('div');
    popupOverlay.classList.add('popup-overlay');
    document.body.appendChild(popupOverlay);

    function closePopup() {
        popup.style.animation = 'fadeOut 0.3s ease-in-out';
        popupOverlay.style.animation = 'fadeOut 0.3s ease-in-out';
        setTimeout(() => {
            popup.style.display = 'none';
            popupOverlay.style.display = 'none';
        }, 300);
    }

    popupClose.addEventListener('click', closePopup);
    popupOverlay.addEventListener('click', closePopup);

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
