// ==========================
// グループ・アイドルデータ
// ==========================
const GROUPS = {
    '月のテンペスト': ['長瀬琴乃', '伊吹渚', '白石沙季', '成宮すず', '早坂芽衣'],
    'サニーピース': ['川咲さくら', '兵藤雫', '白石千紗', '一ノ瀬怜', '佐伯遙子'],
    'TRINITYAiLE': ['天動瑠依', '鈴村優', '奥山すみれ'],
    'LizNoir': ['神崎莉央', '井川葵', '小美山愛', '赤崎こころ'],
    'ⅢX': ['fran', 'kana', 'miho']
};

// フォームの推しピッカーでの表示順（グループに属さない長瀬麻奈は単独枠として表示）
const IDOL_DISPLAY_GROUPS = Object.assign({}, GROUPS, {
    '-': ['長瀬麻奈']
});

// 履歴書カード上でのアイドル表示順（長瀬麻奈はミホの隣に並べる）
const CARD_IDOL_GROUPS = Object.assign({}, GROUPS, {
    'ⅢX': [...GROUPS['ⅢX'], '長瀬麻奈']
});

const UNIONS = ['シリウス', 'カノープス', 'ベガ', 'プロキオン', 'レグルス', 'スピカ', 'アルタイル', 'デネブ'];
const VENUS_RANKS = [
    'BIG4', 'DIAMOND', 'PLATINUM',
    'GOLD 3', 'GOLD 2', 'GOLD 1',
    'SILVER 3', 'SILVER 2', 'SILVER 1',
    'BRONZE 3', 'BRONZE 2', 'BRONZE 1',
    'CHALLENGER 3', 'CHALLENGER 2', 'CHALLENGER 1'
];
const PLAYER_GROUP_MAX = 40;
const GRID_COLUMNS = 5;

// 履歴書カードのテーマカラー（見出し・ラベルのグラデーションに使用する色グループ）
const CARD_THEME_COLOR_GROUPS = [
    ['#5C88DA', '#F56D9E', '#6ACEB9', '#F2EE56', '#E03E52'],
    ['#F69941', '#99C99B', '#E7BBD2', '#ACE3EF', '#C1A7E2'],
    ['#FCFAF1', '#AECE6E', '#FFE495'],
    ['#AE5287', '#6F77CC', '#7ECCEE', '#FC9BB3'],
    ['#F0ED00', '#F251B0']
];

// 単色テーマ（色グループの色を1色ずつ単色で選べるようにしたもの）と、
// グラデーションテーマ（色グループごとの多色グラデーション）の両方を用意
// 選択肢の並び順: デフォルト → 単色 → グラデーション（混ぜた色）
// id は配列の並び順が変わっても保存データが指す色がずれないようにするための安定した識別子
const CARD_THEMES = [
    ...CARD_THEME_COLOR_GROUPS.flat().map(color => ({ type: 'solid', color, id: `solid:${color}` })),
    ...CARD_THEME_COLOR_GROUPS.map((colors, i) => ({ type: 'gradient', colors, id: `gradient:${i}` }))
];

const STORAGE_KEY = 'resumeBuilderData';
const ID_PATTERN = /^[A-Z0-9]{8}$/;

document.addEventListener('DOMContentLoaded', function() {
    const bannerTitle = document.querySelector('.banner_title');
    bannerTitle.addEventListener('click', function() {
        location.href = '../index.html';
    });

    // スクロールトップボタン
    const scrollToTopBtn = document.getElementById('scrollToTopBtn');
    window.addEventListener('scroll', function() {
        scrollToTopBtn.style.display = window.scrollY > 300 ? 'block' : 'none';
    });
    scrollToTopBtn.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // 要素取得
    const fields = {
        playerName: document.getElementById('playerName'),
        managerLv: document.getElementById('managerLv'),
        venusRank: document.getElementById('venusRank'),
        playerGroup: document.getElementById('playerGroup'),
        playerUnion: document.getElementById('playerUnion'),
        startDate: document.getElementById('startDate'),
        startMonth: document.getElementById('startMonth'),
        playerId: document.getElementById('playerId'),
        friendRecruit: document.getElementById('friendRecruit'),
        favSong1: document.getElementById('favSong1'),
        favSong2: document.getElementById('favSong2'),
        favSong3: document.getElementById('favSong3'),
        comment: document.getElementById('comment')
    };
    const startTypeRadios = document.querySelectorAll('input[name="startType"]');
    const playerIdHint = document.getElementById('playerIdHint');

    // ==========================
    // アイコンピッカー（推しグループ・推しアイドル共通の仕組み、人数無制限）
    // ==========================
    function createIconPicker({ pickerEl, cardGridEl, iconPath, iconExt, onChange }) {
        let selected = [];
        const cardIcons = {}; // name -> img要素（カード側）

        function addPickerItem(container, name) {
            const item = document.createElement('label');
            item.className = 'oshi-picker-item';
            item.id = `pick_${container.id}_${name}`;

            const input = document.createElement('input');
            input.type = 'checkbox';
            input.value = name;

            const img = document.createElement('img');
            img.src = `${iconPath}${name}${iconExt}`;
            img.alt = name;
            img.loading = 'lazy';

            const span = document.createElement('span');
            span.textContent = name;

            item.append(input, img, span);
            container.appendChild(item);

            input.addEventListener('change', function() {
                if (input.checked) {
                    selected.push(name);
                } else {
                    selected = selected.filter(n => n !== name);
                }
                syncCardIcons();
                onChange();
            });
        }

        // html2canvas書き出し時にopacityが正しく反映されないため、薄暗さはimg自体ではなく
        // 重ねたベール(rgba背景)の濃さで表現する（wrap要素に'active'クラスを付け外しする）
        function addCardIcon(name) {
            const wrap = document.createElement('div');
            wrap.className = 'resume-oshi-icon';

            const img = document.createElement('img');
            img.alt = name;
            img.loading = 'lazy';
            img.src = `${iconPath}${name}${iconExt}`;

            const veil = document.createElement('div');
            veil.className = 'resume-oshi-veil';

            wrap.append(img, veil);
            cardGridEl.appendChild(wrap);
            cardIcons[name] = wrap;
        }

        // グループの区切りでグリッドの行を揃えるための空白セル
        function addCardSpacer() {
            const spacer = document.createElement('div');
            spacer.className = 'resume-oshi-spacer';
            cardGridEl.appendChild(spacer);
        }

        function syncCardIcons() {
            Object.entries(cardIcons).forEach(([name, wrap]) => {
                wrap.classList.toggle('active', selected.includes(name));
            });
        }

        function setSelected(names) {
            const valid = Array.isArray(names) ? names : [];
            selected = [];
            pickerEl.querySelectorAll('input[type="checkbox"]').forEach(input => {
                const checked = valid.includes(input.value);
                input.checked = checked;
            });
            // 保存されていた選択順を尊重しつつ、実在するものだけに絞る
            const existing = new Set(Array.from(pickerEl.querySelectorAll('input[type="checkbox"]')).map(i => i.value));
            selected = valid.filter(n => existing.has(n));
            syncCardIcons();
        }

        function clear() {
            selected = [];
            pickerEl.querySelectorAll('input[type="checkbox"]').forEach(input => { input.checked = false; });
            syncCardIcons();
        }

        return { addPickerItem, addCardIcon, addCardSpacer, setSelected, clear, getSelected: () => selected };
    }

    // ==========================
    // テーマカラー選択
    // ==========================
    const DEFAULT_THEME_CSS = 'linear-gradient(115deg, #1f00c4 0%, #4b1fff 55%, #6a3bff 100%)';
    const resumeCardEl = document.getElementById('resumeCard');
    const themePickerEl = document.getElementById('themePicker');
    let selectedThemeId = null; // null = デフォルト（紫グラデーション）

    function findThemeById(id) {
        return CARD_THEMES.find(t => t.id === id) || null;
    }

    function buildThemeGradient(colors) {
        if (colors.length === 1) return colors[0];
        const step = 100 / (colors.length - 1);
        const stops = colors.map((c, i) => `${c} ${Math.round(i * step)}%`).join(', ');
        return `linear-gradient(115deg, ${stops})`;
    }

    function themeToCss(theme) {
        return theme.type === 'solid' ? theme.color : buildThemeGradient(theme.colors);
    }

    // テーマを代表する単色（単色テーマはそのまま、グラデーションテーマは1色目を採用）
    function accentHexOf(theme) {
        return theme.type === 'solid' ? theme.color : theme.colors[0];
    }

    // hex色を白に近づけて薄く優しい色にする（ratio: 0=元の色、1=白）
    function lightenHex(hex, ratio) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        const mix = c => Math.round(c + (255 - c) * ratio);
        return `rgb(${mix(r)}, ${mix(g)}, ${mix(b)})`;
    }

    function hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    function buildBgTintGradient(hex) {
        return `linear-gradient(150deg, ${lightenHex(hex, 0.9)} 0%, ${lightenHex(hex, 0.94)} 55%, ${lightenHex(hex, 0.88)} 100%)`;
    }

    // #FCFAF1は明るすぎて白文字が読みにくいため、この色のときだけ黒文字にする
    function isLightColor(hex) {
        return hex.toUpperCase() === '#FCFAF1';
    }

    function applyTheme(id) {
        selectedThemeId = id;
        const theme = id ? findThemeById(id) : null;
        if (!theme) {
            resumeCardEl.style.removeProperty('--theme-gradient');
            resumeCardEl.style.removeProperty('--theme-bg-gradient');
            resumeCardEl.style.removeProperty('--theme-text-color');
            resumeCardEl.style.removeProperty('--theme-icon-ring');
            resumeCardEl.style.removeProperty('--theme-icon-ring-active');
            resumeCardEl.style.removeProperty('--theme-icon-shadow-active');
            return;
        }

        resumeCardEl.style.setProperty('--theme-gradient', themeToCss(theme));

        if (theme.type === 'solid') {
            resumeCardEl.style.setProperty('--theme-bg-gradient', buildBgTintGradient(theme.color));
            if (isLightColor(theme.color)) {
                resumeCardEl.style.setProperty('--theme-text-color', '#333');
            } else {
                resumeCardEl.style.removeProperty('--theme-text-color');
            }
        } else {
            resumeCardEl.style.removeProperty('--theme-bg-gradient');
            resumeCardEl.style.removeProperty('--theme-text-color');
        }

        const accentHex = accentHexOf(theme);
        resumeCardEl.style.setProperty('--theme-icon-ring', hexToRgba(accentHex, 0.08));
        resumeCardEl.style.setProperty('--theme-icon-ring-active', hexToRgba(accentHex, 0.35));
        resumeCardEl.style.setProperty('--theme-icon-shadow-active', hexToRgba(accentHex, 0.2));
    }

    function addThemeSwatch(id, previewCss) {
        const label = document.createElement('label');
        label.className = 'theme-swatch';

        const input = document.createElement('input');
        input.type = 'radio';
        input.name = 'cardTheme';
        input.value = id === null ? '' : id;

        const circle = document.createElement('div');
        circle.className = 'theme-swatch-circle';
        circle.style.background = previewCss;

        label.append(input, circle);
        themePickerEl.appendChild(label);

        input.addEventListener('change', function() {
            if (input.checked) {
                applyTheme(id);
                saveToStorage();
            }
        });
    }

    addThemeSwatch(null, DEFAULT_THEME_CSS);
    CARD_THEMES.forEach(theme => addThemeSwatch(theme.id, themeToCss(theme)));
    themePickerEl.querySelector('input[value=""]').checked = true;

    // 推しグループ
    const groupPickerEl = document.getElementById('groupPicker');
    const groupCardGrid = document.getElementById('resumeGroupGrid');
    const groupPicker = createIconPicker({
        pickerEl: groupPickerEl,
        cardGridEl: groupCardGrid,
        iconPath: '../image/group_icon/',
        iconExt: '.png',
        onChange: updatePreview
    });
    Object.keys(GROUPS).forEach(name => {
        groupPicker.addPickerItem(groupPickerEl, name);
        groupPicker.addCardIcon(name);
    });

    // 推しアイドル
    const oshiPickerEl = document.getElementById('oshiPicker');
    const oshiCardGrid = document.getElementById('resumeIdolGrid');
    const oshiPicker = createIconPicker({
        pickerEl: oshiPickerEl,
        cardGridEl: oshiCardGrid,
        iconPath: '../image/circle_icon/',
        iconExt: '.webp',
        onChange: updatePreview
    });
    Object.entries(IDOL_DISPLAY_GROUPS).forEach(([group, members]) => {
        const label = document.createElement('div');
        label.className = 'oshi-picker-group-label';
        label.textContent = group;
        oshiPickerEl.appendChild(label);
        members.forEach(name => {
            oshiPicker.addPickerItem(oshiPickerEl, name);
        });
    });
    Object.entries(CARD_IDOL_GROUPS).forEach(([group, members]) => {
        members.forEach(name => {
            oshiPicker.addCardIcon(name);
        });
        // カードのグリッドはグループごとに改行させるため、5列に満たない分を空白セルで埋める
        const remainder = members.length % GRID_COLUMNS;
        if (remainder !== 0) {
            for (let i = 0; i < GRID_COLUMNS - remainder; i++) {
                oshiPicker.addCardSpacer();
            }
        }
    });

    // ==========================
    // 所属グループ・所属ユニオン セレクトの構築
    // ==========================
    function populatePlayerGroupSelect() {
        for (let i = 1; i <= PLAYER_GROUP_MAX; i++) {
            const code = String(i).padStart(3, '0');
            const opt = document.createElement('option');
            opt.value = code;
            opt.textContent = code;
            fields.playerGroup.appendChild(opt);
        }
    }

    function populateUnionSelect() {
        UNIONS.forEach(name => {
            const opt = document.createElement('option');
            opt.value = name;
            opt.textContent = name;
            fields.playerUnion.appendChild(opt);
        });
    }

    function populateVenusRankSelect() {
        VENUS_RANKS.forEach(name => {
            const opt = document.createElement('option');
            opt.value = name;
            opt.textContent = name;
            fields.venusRank.appendChild(opt);
        });
    }

    populatePlayerGroupSelect();
    populateUnionSelect();
    populateVenusRankSelect();

    // ==========================
    // 背景画像アップロード
    // ==========================
    const bgImageInput = document.getElementById('bgImage');
    const resumeBgPhoto = document.getElementById('resumeBgPhoto');
    const DEFAULT_BG_IMAGE = '../image/resume-bg.png';

    function setBgImage(url) {
        resumeBgPhoto.style.backgroundImage = `url("${url}")`;
        resumeBgPhoto.style.backgroundSize = '35.5% auto';
        resumeBgPhoto.style.backgroundPosition = 'center';
        resumeBgPhoto.style.backgroundRepeat = 'no-repeat';
    }

    bgImageInput.addEventListener('change', function() {
        const file = bgImageInput.files && bgImageInput.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = function(ev) {
            setBgImage(ev.target.result);
        };
        reader.readAsDataURL(file);
    });

    document.getElementById('clearBgBtn').addEventListener('click', function() {
        bgImageInput.value = '';
        setBgImage(DEFAULT_BG_IMAGE);
    });

    setBgImage(DEFAULT_BG_IMAGE);

    // ==========================
    // Twitterアイコン（任意・未設定時は要素ごと非表示）
    // ==========================
    const twitterIconInput = document.getElementById('twitterIcon');
    const outTwitterIcon = document.getElementById('outTwitterIcon');

    function setTwitterIcon(url) {
        if (url) {
            outTwitterIcon.src = url;
            outTwitterIcon.classList.add('has-icon');
        } else {
            outTwitterIcon.removeAttribute('src');
            outTwitterIcon.classList.remove('has-icon');
        }
    }

    twitterIconInput.addEventListener('change', function() {
        const file = twitterIconInput.files && twitterIconInput.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = function(ev) {
            setTwitterIcon(ev.target.result);
        };
        reader.readAsDataURL(file);
    });

    document.getElementById('clearTwitterIconBtn').addEventListener('click', function() {
        twitterIconInput.value = '';
        setTwitterIcon('');
    });

    // ==========================
    // プレイ開始時期の入力切り替え
    // ==========================
    function updateStartTypeVisibility() {
        const type = document.querySelector('input[name="startType"]:checked')?.value || 'date';
        fields.startDate.style.display = type === 'date' ? '' : 'none';
        fields.startMonth.style.display = type === 'month' ? '' : 'none';
    }

    startTypeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            updateStartTypeVisibility();
            updatePreview();
        });
    });

    // ==========================
    // マネージャーID入力の整形・検証
    // ==========================
    fields.playerId.addEventListener('input', function() {
        const cleaned = fields.playerId.value.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 8);
        fields.playerId.value = cleaned;
        if (cleaned.length === 0) {
            playerIdHint.textContent = '大文字アルファベットと数字で8桁';
            playerIdHint.classList.remove('error');
        } else if (!ID_PATTERN.test(cleaned)) {
            playerIdHint.textContent = `あと${8 - cleaned.length}桁入力してください`;
            playerIdHint.classList.add('error');
        } else {
            playerIdHint.textContent = '入力OK';
            playerIdHint.classList.remove('error');
        }
        updatePreview();
    });

    // ==========================
    // プレビュー更新
    // ==========================
    const out = {
        playerName: document.getElementById('outPlayerNameText'),
        managerLv: document.getElementById('outManagerLv'),
        venusRank: document.getElementById('outVenusRank'),
        playerGroup: document.getElementById('outPlayerGroup'),
        playerUnion: document.getElementById('outPlayerUnion'),
        startPeriod: document.getElementById('outStartPeriod'),
        favSong: document.getElementById('outFavSong'),
        comment: document.getElementById('outComment'),
        playerId: document.getElementById('outPlayerId'),
        friendRecruit: document.getElementById('outFriendRecruit')
    };
    const qrContainer = document.getElementById('qrcode');

    function formatStartPeriod() {
        const type = document.querySelector('input[name="startType"]:checked')?.value || 'date';
        if (type === 'unknown') return '-';
        if (type === 'release') return 'リリース時から';
        if (type === 'month') {
            if (!fields.startMonth.value) return '-';
            const [y, m] = fields.startMonth.value.split('-');
            return `${y}年${parseInt(m, 10)}月ごろ`;
        }
        if (!fields.startDate.value) return '-';
        const [y, m, d] = fields.startDate.value.split('-');
        return `${y}年${parseInt(m, 10)}月${parseInt(d, 10)}日`;
    }

    function updateQr() {
        const id = fields.playerId.value;
        const show = ID_PATTERN.test(id);

        qrContainer.innerHTML = '';
        qrContainer.style.display = show ? 'flex' : 'none';

        if (show && typeof QRCode !== 'undefined') {
            new QRCode(qrContainer, {
                text: id,
                width: 84,
                height: 84,
                colorDark: '#333333',
                colorLight: '#ffffff',
                correctLevel: QRCode.CorrectLevel.M
            });
        }
        out.playerId.textContent = id;
    }

    function updatePreview() {
        out.playerName.textContent = fields.playerName.value.trim() || '-';
        out.managerLv.textContent = fields.managerLv.value ? `Lv.${fields.managerLv.value}` : '-';
        out.venusRank.textContent = fields.venusRank.value || '-';
        out.playerGroup.textContent = fields.playerGroup.value || '-';
        out.playerUnion.textContent = fields.playerUnion.value || '-';
        out.friendRecruit.textContent = fields.friendRecruit.value || '-';
        out.startPeriod.textContent = formatStartPeriod();

        const songs = [fields.favSong1.value, fields.favSong2.value, fields.favSong3.value]
            .map(s => s.trim())
            .filter(Boolean);
        out.favSong.textContent = songs.length ? songs.join('\n') : '-';

        out.comment.textContent = fields.comment.value.trim() || '-';

        updateQr();
        saveToStorage();
    }

    ['playerName', 'managerLv', 'startDate', 'startMonth', 'favSong1', 'favSong2', 'favSong3', 'comment'].forEach(key => {
        fields[key].addEventListener('input', updatePreview);
    });
    fields.playerGroup.addEventListener('change', updatePreview);
    fields.playerUnion.addEventListener('change', updatePreview);
    fields.venusRank.addEventListener('change', updatePreview);
    fields.friendRecruit.addEventListener('change', updatePreview);

    // ==========================
    // 入力内容の保存・復元
    // ==========================
    function saveToStorage() {
        const data = {
            playerName: fields.playerName.value,
            managerLv: fields.managerLv.value,
            venusRank: fields.venusRank.value,
            playerGroup: fields.playerGroup.value,
            playerUnion: fields.playerUnion.value,
            startType: document.querySelector('input[name="startType"]:checked')?.value || 'date',
            startDate: fields.startDate.value,
            startMonth: fields.startMonth.value,
            playerId: fields.playerId.value,
            friendRecruit: fields.friendRecruit.value,
            cardTheme: selectedThemeId,
            selectedGroups: groupPicker.getSelected(),
            selectedOshi: oshiPicker.getSelected(),
            favSong1: fields.favSong1.value,
            favSong2: fields.favSong2.value,
            favSong3: fields.favSong3.value,
            comment: fields.comment.value
        };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    }

    function loadFromStorage() {
        let data;
        try {
            data = JSON.parse(localStorage.getItem(STORAGE_KEY));
        } catch (e) {
            data = null;
        }
        if (!data) return;

        fields.playerName.value = data.playerName || '';
        fields.managerLv.value = data.managerLv || '';
        fields.venusRank.value = data.venusRank || '';
        fields.playerGroup.value = data.playerGroup || '';
        fields.playerUnion.value = data.playerUnion || '';
        fields.startDate.value = data.startDate || '';
        fields.startMonth.value = data.startMonth || '';
        fields.playerId.value = data.playerId || '';
        fields.friendRecruit.value = data.friendRecruit || '';

        // cardThemeは色を指すidの文字列で保存する。過去バージョンで配列の添字（数値）が
        // 保存されていた場合は、並び順の変更で別の色を指してしまう恐れがあるため破棄する
        const themeId = (typeof data.cardTheme === 'string' && findThemeById(data.cardTheme)) ? data.cardTheme : null;
        applyTheme(themeId);
        const themeRadioValue = themeId === null ? '' : themeId;
        const themeRadio = themePickerEl.querySelector(`input[value="${themeRadioValue}"]`);
        if (themeRadio) themeRadio.checked = true;

        fields.favSong1.value = data.favSong1 || '';
        fields.favSong2.value = data.favSong2 || '';
        fields.favSong3.value = data.favSong3 || '';
        fields.comment.value = data.comment || '';

        const startType = data.startType || 'date';
        const radioToCheck = document.querySelector(`input[name="startType"][value="${startType}"]`);
        if (radioToCheck) radioToCheck.checked = true;
        updateStartTypeVisibility();

        groupPicker.setSelected(data.selectedGroups);
        oshiPicker.setSelected(data.selectedOshi);
    }

    loadFromStorage();
    updatePreview();

    // ==========================
    // リセット
    // ==========================
    document.getElementById('resetBtn').addEventListener('click', function() {
        if (!confirm('入力内容をリセットしますか？')) return;
        localStorage.removeItem(STORAGE_KEY);
        Object.values(fields).forEach(el => { el.value = ''; });
        document.querySelector('input[name="startType"][value="date"]').checked = true;
        updateStartTypeVisibility();
        groupPicker.clear();
        oshiPicker.clear();
        bgImageInput.value = '';
        setBgImage(DEFAULT_BG_IMAGE);
        twitterIconInput.value = '';
        setTwitterIcon('');
        applyTheme(null);
        themePickerEl.querySelector('input[value=""]').checked = true;
        playerIdHint.textContent = '大文字アルファベットと数字で8桁';
        playerIdHint.classList.remove('error');
        updatePreview();
    });

    // ==========================
    // 画像として保存(横16:9・高解像度で書き出し)
    // ==========================
    document.getElementById('downloadBtn').addEventListener('click', function() {
        const card = document.getElementById('resumeCard');
        const targetWidth = 3200; // 16:9で3200x1800相当の解像度を確保
        const scale = Math.min(6, Math.max(1, targetWidth / card.offsetWidth));

        // html2canvasの非同期処理が終わってからwindow.openすると「ユーザー操作起因」と
        // 認識されずスマホブラウザにブロックされるため、クリック直後・同期的にタブを開いておく
        const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
        const newTab = isMobile ? window.open('', '_blank') : null;
        if (newTab) newTab.document.write('画像を生成中です…しばらくお待ちください。');

        html2canvas(card, { scale, backgroundColor: '#ffffff', useCORS: true })
            .then(canvas => finishImageSave(canvas, 'idoly_resume.png', newTab))
            .catch(err => {
                console.error('画像の生成に失敗しました: ', err);
                if (newTab) newTab.close();
            });
    });

    function finishImageSave(canvas, filename, preOpenedTab) {
        canvas.toBlob(blob => {
            if (!blob) {
                if (preOpenedTab) preOpenedTab.close();
                return;
            }
            const url = URL.createObjectURL(blob);
            if (preOpenedTab) {
                preOpenedTab.location.href = url;
            } else {
                const link = document.createElement('a');
                link.download = filename;
                link.href = url;
                link.click();
            }
            setTimeout(() => URL.revokeObjectURL(url), 30000);
        }, 'image/png');
    }
});
