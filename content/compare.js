function esc(value) {
    return String(value ?? '').replace(/[&<>"']/g, ch => (
        { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]
    ));
}

function escRich(value) {
    // スキル効果文など、意図的に<br>改行タグだけを含むテキスト用のエスケープ
    return esc(value).replace(/&lt;br&gt;/g, '<br>');
}

function getCard(key) {
    return ALL_CARDS.find(c => c.key === key) || null;
}

function bestClass(vals, idx) {
    const max = Math.max(...vals);
    return vals[idx] === max ? 'stat-best' : '';
}

function trendColor(trend) {
    if (trend === 'ボーカル') return '#FF469D';
    if (trend === 'ダンス') return '#3ABAFF';
    if (trend === 'ビジュアル') return '#FFA900';
    return '';
}

const selectedCards = { 1: null, 2: null, 3: null, 4: null, 5: null };

function initCombobox(slot) {
    const combo = document.getElementById(`combo-${slot}`);
    const isOptional = combo.dataset.optional === 'true';

    const input = document.createElement('input');
    input.type = 'text';
    input.id = `combo-${slot}-input`;
    input.className = 'combo-input';
    input.placeholder = 'カード名・キャラ名で検索';
    input.autocomplete = 'off';
    input.setAttribute('role', 'combobox');
    input.setAttribute('aria-autocomplete', 'list');
    input.setAttribute('aria-expanded', 'false');

    const dropdownId = `combo-${slot}-dropdown`;
    const dropdown = document.createElement('div');
    dropdown.className = 'combo-dropdown';
    dropdown.id = dropdownId;
    dropdown.setAttribute('role', 'listbox');
    input.setAttribute('aria-controls', dropdownId);

    combo.appendChild(input);
    combo.appendChild(dropdown);

    let activeIdx = -1;

    function getOptions() {
        return Array.from(dropdown.querySelectorAll('.combo-option'));
    }

    function setActive(idx) {
        const opts = getOptions();
        opts.forEach((el, i) => el.classList.toggle('keyboard-focused', i === idx));
        activeIdx = idx;
        if (opts[idx]) opts[idx].scrollIntoView({ block: 'nearest' });
    }

    function selectOption(optEl) {
        const value = optEl.dataset.value;
        selectedCards[slot] = value || null;
        input.value = value ? optEl.textContent : '';
        dropdown.style.display = 'none';
        input.setAttribute('aria-expanded', 'false');
        activeIdx = -1;
        renderCompare();
        updateUrl();
    }

    function renderDropdown(query) {
        const q = (query || '').toLowerCase();
        dropdown.innerHTML = '';
        activeIdx = -1;

        if (isOptional) {
            const noneEl = document.createElement('div');
            noneEl.className = 'combo-option';
            noneEl.setAttribute('role', 'option');
            noneEl.textContent = 'なし';
            noneEl.dataset.value = '';
            dropdown.appendChild(noneEl);
        }

        const groups = {};
        ALL_CARDS.forEach(card => {
            if (!q || card.char.includes(q) || card.card.includes(q)) {
                if (!groups[card.char]) groups[card.char] = [];
                groups[card.char].push(card);
            }
        });

        Object.entries(groups).forEach(([char, cards]) => {
            const groupEl = document.createElement('div');
            groupEl.className = 'combo-group';
            groupEl.textContent = char;
            dropdown.appendChild(groupEl);
            cards.forEach(card => {
                const optEl = document.createElement('div');
                optEl.className = 'combo-option'
                    + (card.key === selectedCards[slot] ? ' selected' : '')
                    + (card.incomplete ? ' data-incomplete' : '');
                optEl.setAttribute('role', 'option');
                optEl.textContent = `${card.card} ${card.char}`;
                optEl.dataset.value = card.key;
                dropdown.appendChild(optEl);
            });
        });

        dropdown.style.display = 'block';
        input.setAttribute('aria-expanded', 'true');
    }

    input.addEventListener('focus', () => renderDropdown(input.value));
    input.addEventListener('input', () => {
        if (!input.value) {
            selectedCards[slot] = null;
            renderCompare();
            updateUrl();
        }
        renderDropdown(input.value);
    });
    input.addEventListener('blur', () => {
        setTimeout(() => {
            dropdown.style.display = 'none';
            input.setAttribute('aria-expanded', 'false');
            activeIdx = -1;
        }, 150);
    });
    input.addEventListener('keydown', e => {
        const isOpen = dropdown.style.display !== 'none';
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (!isOpen) renderDropdown(input.value);
            setActive(Math.min(activeIdx + 1, getOptions().length - 1));
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (!isOpen) return;
            setActive(Math.max(activeIdx - 1, 0));
        } else if (e.key === 'Enter') {
            if (!isOpen) return;
            const opts = getOptions();
            if (activeIdx >= 0 && opts[activeIdx]) {
                e.preventDefault();
                selectOption(opts[activeIdx]);
            }
        } else if (e.key === 'Escape') {
            dropdown.style.display = 'none';
            input.setAttribute('aria-expanded', 'false');
            activeIdx = -1;
        }
    });

    dropdown.addEventListener('mousedown', e => {
        const optEl = e.target.closest('.combo-option');
        if (!optEl) return;
        selectOption(optEl);
    });
}

function renderCompare() {
    const keys = [selectedCards[1], selectedCards[2], selectedCards[3], selectedCards[4], selectedCards[5]].filter(k => k);

    const result = document.getElementById('compare-result');

    if (keys.length < 2) {
        result.innerHTML = '<p class="hint">カードを2枚以上選択してください。</p>';
        return;
    }

    const cards = keys.map(k => getCard(k)).filter(Boolean);
    const n = cards.length;

    // ヘッダー行
    let headerHtml = '<tr><th>項目</th>';
    cards.forEach(c => {
        headerHtml += `<th>
            <img src="../image/idol/${esc(c.char)} ${esc(c.card)}.webp" class="card-icon" alt="${esc(c.card)} ${esc(c.char)}" onerror="this.style.display='none'">
            <a href="../detail/${esc(c.char)} ${esc(c.card)}.html">${esc(c.card)}<br>${esc(c.char)}</a>
            ${c.incomplete ? '<div class="compare-incomplete-notice">⚠ 未入力項目あり</div>' : ''}
        </th>`;
    });
    headerHtml += '</tr>';

    // 基本情報
    const infoFields = [
        ['初期レアリティ', c => esc(c.rarity)],
        ['傾向', c => `<span style="color:${trendColor(c.trend)};font-weight:bold">${esc(c.trend)}</span>`],
        ['タイプ', c => esc(c.type)],
        ['スキル構成', c => esc(c.skills_comp)],
        ['エール', c => `<img src="../image/yell/${esc(c.yell)}.webp" style="height:32px" alt="" onerror="this.style.display='none'"> ${esc(c.yell)}`],
        ['入手方法', c => esc(c.obtain)],
        ['実装日', c => esc(c.release_date)],
    ];

    let infoHtml = '';
    infoFields.forEach(([label, fn]) => {
        infoHtml += `<tr><th>${label}</th>`;
        cards.forEach(c => { infoHtml += `<td>${fn(c)}</td>`; });
        infoHtml += '</tr>';
    });

    // ステータス
    const statKeys = ['vocal', 'dance', 'visual', 'stamina', 'power'];
    const statLabels = {
        vocal: '<span style="color:#FF469D">ボーカル</span>',
        dance: '<span style="color:#3ABAFF">ダンス</span>',
        visual: '<span style="color:#FFA900">ビジュアル</span>',
        stamina: 'スタミナ',
        power: 'パワー',
    };

    let statsHtml = '';
    statKeys.forEach(key => {
        const vals = cards.map(c => c[key]);
        statsHtml += `<tr><th>${statLabels[key]}</th>`;
        cards.forEach((c, i) => {
            statsHtml += `<td class="${bestClass(vals, i)}">${c[key]}</td>`;
        });
        statsHtml += '</tr>';
    });

    // スキル
    const skillSlots = [
        ['スキル1', 'skill1_name', 'skill1_effect'],
        ['スキル2', 'skill2_name', 'skill2_effect'],
        ['スキル3', 'skill3_name', 'skill3_effect'],
        ['覚醒スキル', 'awakening_name', 'awakening_effect'],
    ];

    let skillsHtml = '';
    skillSlots.forEach(([label, nameKey, effectKey]) => {
        if (!cards.some(c => c[nameKey])) return;
        skillsHtml += `<tr class="skill-row"><th>${label}</th>`;
        cards.forEach(c => {
            skillsHtml += c[nameKey]
                ? `<td><strong>${esc(c[nameKey])}</strong><br><span class="skill-effect">${escRich(c[effectKey])}</span></td>`
                : '<td>-</td>';
        });
        skillsHtml += '</tr>';
    });

    result.innerHTML = `
        <table class="compare-table">
            <thead>${headerHtml}</thead>
            <tbody>
                <tr class="section-header"><td colspan="${n + 1}">基本情報</td></tr>
                ${infoHtml}
                <tr class="section-header"><td colspan="${n + 1}">ステータス</td></tr>
                ${statsHtml}
                <tr class="section-header"><td colspan="${n + 1}">ライブスキル</td></tr>
                ${skillsHtml}
            </tbody>
        </table>`;
}

function updateUrl() {
    const params = new URLSearchParams();
    [1,2,3,4,5].forEach(i => { if (selectedCards[i]) params.set(`c${i}`, selectedCards[i]); });
    const qs = params.toString();
    history.replaceState(null, '', qs ? `?${qs}` : location.pathname);
}

function copyCompareUrl() {
    navigator.clipboard.writeText(location.href).then(function() {
        const msg = document.getElementById('copy-url-msg');
        if (msg) {
            msg.style.display = 'inline';
            setTimeout(function() { msg.style.display = 'none'; }, 2000);
        }
    });
}

function loadFromUrl() {
    const params = new URLSearchParams(location.search);
    [1, 2, 3, 4, 5].forEach(slot => {
        const key = params.get(`c${slot}`);
        if (!key) return;
        const card = ALL_CARDS.find(c => c.key === key);
        if (!card) return;
        selectedCards[slot] = key;
        const input = document.querySelector(`#combo-${slot} .combo-input`);
        if (input) input.value = `${card.card} ${card.char}`;
    });
    renderCompare();
}

document.addEventListener('DOMContentLoaded', () => {
    initCombobox(1);
    initCombobox(2);
    initCombobox(3);
    initCombobox(4);
    initCombobox(5);

    loadFromUrl();

    const scrollBtn = document.getElementById('scrollToTopBtn');
    window.addEventListener('scroll', () => {
        scrollBtn.style.display = document.documentElement.scrollTop > 100 ? 'block' : 'none';
    });
    scrollBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
});
