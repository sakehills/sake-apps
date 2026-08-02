
        document.addEventListener('DOMContentLoaded', () => {
            let sakeData = [];
            const grid = document.getElementById('sakeGrid');
            const searchInput = document.getElementById('searchInput');
            const breweryFilter = document.getElementById('breweryFilter');
            const typeFilter = document.getElementById('typeFilter');
            const ssiFilter = document.getElementById('ssiFilter');
            const imageFilter = document.getElementById('imageFilter');
            const sortOrder = document.getElementById('sortOrder');
            
            // ① 詳細
            const detailModal = document.getElementById('detailModal');
            const detailImg = document.getElementById('detailImg');
            const detailImgLabel = document.getElementById('detailImgLabel');
            const detailImgToggle = document.getElementById('detailImgToggle');
            const openSpecsEditBtn = document.getElementById('openSpecsEditBtn');
            const mapPinAvg = document.getElementById('mapPinAvg');
            const mapUserDots = document.getElementById('mapUserDots');
            
            // ② 編集
            const editModal = document.getElementById('editModal');
            const editTitle = document.getElementById('editTitle');
            const editForm = document.getElementById('editForm');
            const editProductId = document.getElementById('editProductId');
            const editBodyLevel = document.getElementById('editBodyLevel');
            const editAromaLevel = document.getElementById('editAromaLevel');
            const editComment = document.getElementById('editComment');
            const editSsiGroup = document.getElementById('editSsiGroup');
            const editImageInput = document.getElementById('editImageInput');
            const editImagePreviewContainer = document.getElementById('editImagePreviewContainer');
            const editImagePreviewImg = document.getElementById('editImagePreviewImg');
            const editImageClearBtn = document.getElementById('editImageClearBtn');
            const editSubmitBtn = document.getElementById('editSubmitBtn');
            const editDeleteBtn = document.getElementById('editDeleteBtn');
            const editTotalScore = document.getElementById('editTotalScore');
            const editTasteScore = document.getElementById('editTasteScore');
            const editAromaScore = document.getElementById('editAromaScore');
             
            // スライダー用追加要素
            const valTotalScore = document.getElementById('valTotalScore');
            const valTasteScore = document.getElementById('valTasteScore');
            const valAromaScore = document.getElementById('valAromaScore');
            const noTasteScore = document.getElementById('noTasteScore');
            const noAromaScore = document.getElementById('noAromaScore');
             
            // スライダー値連動と無効化制御
            setTimeout(() => {
                 editTotalScore.addEventListener('input', function() {
                     valTotalScore.textContent = parseFloat(this.value).toFixed(1);
                 });
                 editTasteScore.addEventListener('input', function() {
                     valTasteScore.textContent = parseFloat(this.value).toFixed(1);
                 });
                 editAromaScore.addEventListener('input', function() {
                     valAromaScore.textContent = parseFloat(this.value).toFixed(1);
                 });
                 
                 noTasteScore.addEventListener('change', function() {
                     editTasteScore.disabled = this.checked;
                     if (this.checked) {
                         editTasteScore.style.opacity = 0.4;
                         valTasteScore.style.opacity = 0.4;
                         valTasteScore.textContent = "--";
                     } else {
                         editTasteScore.style.opacity = 1;
                         valTasteScore.style.opacity = 1;
                         valTasteScore.textContent = parseFloat(editTasteScore.value).toFixed(1);
                     }
                 });
                 noAromaScore.addEventListener('change', function() {
                     editAromaScore.disabled = this.checked;
                     if (this.checked) {
                         editAromaScore.style.opacity = 0.4;
                         valAromaScore.style.opacity = 0.4;
                         valAromaScore.textContent = "--";
                     } else {
                         editAromaScore.style.opacity = 1;
                         valAromaScore.style.opacity = 1;
                         valAromaScore.textContent = parseFloat(editAromaScore.value).toFixed(1);
                     }
                 });
             }, 0);
            
            // ③ 他者レビュー
            const othersModal = document.getElementById('othersModal');
            const othersTitle = document.getElementById('othersTitle');
            const othersTimeline = document.getElementById('othersTimeline');

            // ④ スペック手動編集
            const specsEditModal = document.getElementById('specsEditModal');
            const specsEditForm = document.getElementById('specsEditForm');
            const specsEditId = document.getElementById('specsEditId');
            
            const NO_IMAGE_PLACEHOLDER = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMzAwIiB2aWV3Qm94PSIwIDAgMjAwIDMwMCI+PHJlY3Qgd2lkdGg9IjIwMCIgaGVpZ2h0PSIzMDAiIGZpbGw9IiMxNDFkMmYiIHJ4PSIxMiIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjNjQ3NDhiIiBmb250LWZhbWlseT0ic2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZm9udC13ZWlnaHQ9ImJvbGQiPueUu+WDj+acqueZu+mMsjwvdGV4dD48L3N2Zz4=';

            // 星評価表示用の汎用ヘルパー関数
            function getStarHtml(score) {
                if (score === undefined || score === null) return '';
                let stars = '';
                const rounded = Math.round(score);
                for (let i = 1; i <= 5; i++) {
                    if (rounded >= i) {
                        stars += '★';
                    } else {
                        stars += '☆';
                    }
                }
                return `<span style="color: var(--accent); font-weight: 700; margin-right: 0.5rem; letter-spacing: 1px;">${stars} ${score.toFixed(1)}</span>`;
            }

            const specsEditCategory = document.getElementById('specsEditCategory');
            const specsEditAlcohol = document.getElementById('specsEditAlcohol');
            const specsEditPolish = document.getElementById('specsEditPolish');
            const specsEditIngredients = document.getElementById('specsEditIngredients');
            const specsEditVariety = document.getElementById('specsEditVariety');
            const specsEditYeast = document.getElementById('specsEditYeast');
            const specsEditSmv = document.getElementById('specsEditSmv');
            const specsEditAcidity = document.getElementById('specsEditAcidity');
            const specsEditAmino = document.getElementById('specsEditAmino');
            const specsFrontImageInput = document.getElementById('specsFrontImageInput');
            const specsFrontPreviewContainer = document.getElementById('specsFrontPreviewContainer');
            const specsFrontPreviewImg = document.getElementById('specsFrontPreviewImg');
            const specsFrontClearBtn = document.getElementById('specsFrontClearBtn');
            const specsBackImageInput = document.getElementById('specsBackImageInput');
            const specsBackPreviewContainer = document.getElementById('specsBackPreviewContainer');
            const specsBackPreviewImg = document.getElementById('specsBackPreviewImg');
            const specsBackClearBtn = document.getElementById('specsBackClearBtn');
            const aiSuggestBtn = document.getElementById('aiSuggestBtn');
            const aiSuggestLoading = document.getElementById('aiSuggestLoading');
            
            // ページネーション用の状態変数
            let currentPage = 1;
            const itemsPerPage = 50;
            let filteredData = [];

            const btnFirst = document.getElementById('btnFirst');
            const btnPrev = document.getElementById('btnPrev');
            const btnNext = document.getElementById('btnNext');
            const btnLast = document.getElementById('btnLast');
            const pageInfo = document.getElementById('pageInfo');

            let currentSake = null;
            let showFrontImage = true;
            let selectedSsiType = "";
            let attachedImageBase64 = "";

            // スペック編集用の画像Base64状態
            let specsFrontImageBase64 = null;
            let specsBackImageBase64 = null;

            // 初期化
            async function init() {
                try {
                    grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 4rem 0;">データベースから日本酒情報を読み込み中...</div>';
                    const response = await fetch('/api/products');
                    if (!response.ok) throw new Error('API取得に失敗しました');
                    sakeData = await response.json();
                } catch(err) {
                    grid.innerHTML = `<div class="no-data" style="grid-column: 1/-1; text-align: center; color: var(--danger); padding: 4rem 0;">お酒データの取得に失敗しました: ${err.message}</div>`;
                    return;
                }
                
                setupFilters();
                
                // イベントリスナー
                searchInput.addEventListener('input', filterData);
                breweryFilter.addEventListener('change', filterData);
                typeFilter.addEventListener('change', filterData);
                ssiFilter.addEventListener('change', filterData);
                imageFilter.addEventListener('change', filterData);
                sortOrder.addEventListener('change', filterData);
                
                detailImgToggle.addEventListener('click', toggleDetailImage);
                
                // スペック編集モーダルを開く
                openSpecsEditBtn.addEventListener('click', openSpecsEditModal);
                
                // ページネーションボタン
                btnFirst.addEventListener('click', () => { currentPage = 1; renderPage(); });
                btnPrev.addEventListener('click', () => { if (currentPage > 1) { currentPage--; renderPage(); } });
                btnNext.addEventListener('click', () => { 
                    const totalPages = Math.ceil(filteredData.length / itemsPerPage) || 1;
                    if (currentPage < totalPages) { currentPage++; renderPage(); } 
                });
                btnLast.addEventListener('click', () => { 
                    const totalPages = Math.ceil(filteredData.length / itemsPerPage) || 1;
                    currentPage = totalPages; 
                    renderPage(); 
                });
                
                // 画像アップロード時の読み込み処理 (口コミ用)
                editImageInput.addEventListener('change', (e) => {
                    const file = e.target.files[0];
                    if (!file) return;
                    
                    const reader = new FileReader();
                    reader.onload = function(event) {
                        attachedImageBase64 = event.target.result;
                        editImagePreviewImg.src = attachedImageBase64;
                        editImagePreviewContainer.style.display = 'block';
                    };
                    reader.readAsDataURL(file);
                });
                
                editImageClearBtn.addEventListener('click', () => {
                    attachedImageBase64 = "";
                    editImageInput.value = "";
                    editImagePreviewContainer.style.display = 'none';
                    editImagePreviewImg.src = "";
                });

                // スペック手動編集時の画像アップロード処理
                specsFrontImageInput.addEventListener('change', (e) => {
                    const file = e.target.files[0];
                    if (!file) return;
                    const reader = new FileReader();
                    reader.onload = function(event) {
                        specsFrontImageBase64 = event.target.result;
                        specsFrontPreviewImg.src = specsFrontImageBase64;
                        specsFrontPreviewContainer.style.display = 'block';
                    };
                    reader.readAsDataURL(file);
                });
                specsFrontClearBtn.addEventListener('click', () => {
                    specsFrontImageBase64 = ""; // 空文字でサーバーへ送信＝削除
                    specsFrontImageInput.value = "";
                    specsFrontPreviewContainer.style.display = 'none';
                });

                specsBackImageInput.addEventListener('change', (e) => {
                    const file = e.target.files[0];
                    if (!file) return;
                    const reader = new FileReader();
                    reader.onload = function(event) {
                        specsBackImageBase64 = event.target.result;
                        specsBackPreviewImg.src = specsBackImageBase64;
                        specsBackPreviewContainer.style.display = 'block';
                    };
                    reader.readAsDataURL(file);
                });
                specsBackClearBtn.addEventListener('click', () => {
                    specsBackImageBase64 = ""; // 空文字でサーバーへ送信＝削除
                    specsBackImageInput.value = "";
                    specsBackPreviewContainer.style.display = 'none';
                });
                // AIスペック提案自動取得
                aiSuggestBtn.addEventListener('click', async () => {
                    const productId = parseInt(specsEditId.value);
                    if (!productId) return;
                    
                    aiSuggestBtn.disabled = true;
                    aiSuggestBtn.style.opacity = 0.5;
                    aiSuggestLoading.style.display = 'inline-flex';
                    
                    try {
                        const response = await fetch('/api/product/suggest', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ product_id: productId })
                        });
                        
                        if (!response.ok) throw new Error('AI提案の取得に失敗しました');
                        const result = await response.json();
                        
                        if (result.status === 'success' && result.data) {
                            const spec = result.data;
                            
                            // フォームに反映
                            if (spec.category) specsEditCategory.value = spec.category;
                            if (spec.alcohol) specsEditAlcohol.value = spec.alcohol;
                            if (spec.polish_ratio) specsEditPolish.value = spec.polish_ratio;
                            if (spec.ingredients) specsEditIngredients.value = spec.ingredients;
                            if (spec.rice_variety) specsEditVariety.value = spec.rice_variety;
                            if (spec.yeast) specsEditYeast.value = spec.yeast;
                            if (spec.smv) specsEditSmv.value = spec.smv;
                            if (spec.acidity) specsEditAcidity.value = spec.acidity;
                            if (spec.amino_acidity) specsEditAmino.value = spec.amino_acidity;
                            
                            alert('AIがWeb情報からスペック情報を自動抽出・入力しました！内容を確認し、問題なければ保存してください。');
                        } else {
                            throw new Error(result.message || 'データが空です');
                        }
                    } catch (err) {
                        alert('AI自動入力中にエラーが発生しました: ' + err.message);
                    } finally {
                        aiSuggestBtn.disabled = false;
                        aiSuggestBtn.style.opacity = 1;
                        aiSuggestLoading.style.display = 'none';
                    }
                });
                
                // SSI 4タイプ選択
                editSsiGroup.querySelectorAll('.ssi-btn').forEach(btn => {
                    btn.addEventListener('click', () => {
                        editSsiGroup.querySelectorAll('.ssi-btn').forEach(b => b.classList.remove('active'));
                        if (selectedSsiType === btn.dataset.type) {
                            selectedSsiType = "";
                        } else {
                            btn.classList.add('active');
                            selectedSsiType = btn.dataset.type;
                        }
                    });
                });
                
                // コメント送信
                editForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    
                    const payload = {
                        product_id: parseInt(editProductId.value),
                        user_name: 'hitocie',
                        ssi_type: selectedSsiType,
                        body_level: editBodyLevel.value,
                        aroma_level: editAromaLevel.value,
                        comment: editComment.value,
                        rating_image: attachedImageBase64,
                        user_id: 'test_seed_secondary_sources',
                        total_score: parseFloat(editTotalScore.value),
                        taste_score: noTasteScore.checked ? null : parseFloat(editTasteScore.value),
                        aroma_score: noAromaScore.checked ? null : parseFloat(editAromaScore.value)
                    };
                    
                    try {
                        const response = await fetch('/api/rate', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(payload)
                        });
                        
                        if (response.ok) {
                            alert('評価を保存しました。');
                            window.location.reload();
                        } else {
                            alert('保存に失敗しました。');
                        }
                    } catch (err) {
                        alert('通信エラーが発生しました。');
                    }
                });
                
                // コメント削除
                editDeleteBtn.addEventListener('click', async () => {
                    if (!confirm('本当にこのコメントを削除しますか？')) return;
                    
                    const payload = {
                        product_id: parseInt(editProductId.value),
                        user_name: 'hitocie'
                    };
                    
                    try {
                        const response = await fetch('/api/rate/delete', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(payload)
                        });
                        
                        if (response.ok) {
                            alert('削除しました。');
                            window.location.reload();
                        } else {
                            alert('削除に失敗しました。');
                        }
                    } catch (err) {
                        alert('削除通信エラーが発生しました。');
                    }
                });

                // スペック手動編集送信
                specsEditForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    
                    const payload = {
                        id: parseInt(specsEditId.value),
                        category: specsEditCategory.value,
                        alcohol: parseFloat(specsEditAlcohol.value) || null,
                        polish_ratio: specsEditPolish.value,
                        ingredients: specsEditIngredients.value,
                        rice_variety: specsEditVariety.value,
                        yeast: specsEditYeast.value,
                        smv: specsEditSmv.value,
                        acidity: specsEditAcidity.value,
                        amino_acidity: specsEditAmino.value,
                        cropped_image_path_front: specsFrontImageBase64,
                        cropped_image_path_back: specsBackImageBase64
                    };
                    
                    try {
                        const response = await fetch('/api/product/update', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(payload)
                        });
                        
                        if (response.ok) {
                            alert('スペック情報を保存しました。');
                            window.location.reload();
                        } else {
                            alert('スペック情報の保存に失敗しました。');
                        }
                    } catch (err) {
                        alert('スペック保存通信エラーが発生しました。');
                    }
                });

                // 初期フィルタ＆レンダリング実行
                filterData();
            }

            // 検索とフィルター、ソートの適用
            function filterData() {
                const query = searchInput.value.toLowerCase();
                const selectedBrewery = breweryFilter.value;
                const selectedType = typeFilter.value;
                const selectedSsi = ssiFilter.value;
                const imageState = imageFilter.value;
                const sortType = sortOrder.value;
                
                filteredData = sakeData.filter(item => {
                    const matchesSearch = 
                        item.name.toLowerCase().includes(query) ||
                        (item.sub_name && item.sub_name.toLowerCase().includes(query)) ||
                        (item.brewery && item.brewery.toLowerCase().includes(query)) ||
                        (item.sake_type && item.sake_type.toLowerCase().includes(query));
                        
                    const matchesBrewery = !selectedBrewery || item.brewery === selectedBrewery;
                    const matchesType = !selectedType || item.sake_type === selectedType;
                    
                    const ssi = item.ssi_type || (item.ratings && item.ratings.length > 0 ? item.ratings[0].ssi_type : "");
                    const matchesSsi = !selectedSsi || ssi === selectedSsi;
                    
                    const hasImage = !!(item.cropped_image_path_front);
                    const matchesImage = !imageState || 
                        (imageState === 'has_image' && hasImage) || 
                        (imageState === 'no_image' && !hasImage);
                        
                    return matchesSearch && matchesBrewery && matchesType && matchesSsi && matchesImage;
                });
                
                if (sortType === 'id_asc') {
                    filteredData.sort((a, b) => a.id - b.id);
                } else if (sortType === 'id_desc') {
                    filteredData.sort((a, b) => b.id - a.id);
                } else if (sortType === 'alcohol_desc') {
                    filteredData.sort((a, b) => (b.alcohol_content || 0) - (a.alcohol_content || 0));
                } else if (sortType === 'alcohol_asc') {
                    filteredData.sort((a, b) => (a.alcohol_content || 0) - (b.alcohol_content || 0));
                } else if (sortType === 'reviews_desc') {
                    filteredData.sort((a, b) => {
                        const lenA = a.ratings ? a.ratings.length : 0;
                        const lenB = b.ratings ? b.ratings.length : 0;
                        return lenB - lenA;
                    });
                } else if (sortType === 'name_asc') {
                    filteredData.sort((a, b) => a.name.localeCompare(b.name, 'ja'));
                }
                
                currentPage = 1;
                renderPage();
            }

            // ページごとのスライスレンダリング (DOM描画の最適化)
            function renderPage() {
                grid.innerHTML = '';
                const totalItems = filteredData.length;
                const totalPages = Math.ceil(totalItems / itemsPerPage) || 1;
                
                if (currentPage > totalPages) currentPage = totalPages;
                if (currentPage < 1) currentPage = 1;
                
                const startIdx = (currentPage - 1) * itemsPerPage;
                const endIdx = Math.min(startIdx + itemsPerPage, totalItems);
                
                const pageSlice = filteredData.slice(startIdx, endIdx);
                
                btnFirst.disabled = (currentPage === 1);
                btnPrev.disabled = (currentPage === 1);
                btnNext.disabled = (currentPage === totalPages);
                btnLast.disabled = (currentPage === totalPages);
                
                pageInfo.textContent = `${currentPage} / ${totalPages} ページ (合計 ${totalItems}件)`;
                
                if (pageSlice.length === 0) {
                    grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 4rem 0;">該当する日本酒がありません。</div>';
                    return;
                }
                
                pageSlice.forEach(item => {
                    const card = document.createElement('div');
                    card.className = 'sake-card';
                    
                    const othersCount = item.ratings ? item.ratings.filter(r => r.user_name !== 'hitocie').length : 0;
                    const hasMyComment = item.ratings ? item.ratings.some(r => r.user_name === 'hitocie') : false;
                    const editBtnText = hasMyComment ? '✍️ コメントを修正' : '➕ コメントを追加';
                    
                    let indicatorHtml = '';
                    if (othersCount > 0) {
                        indicatorHtml = `<div class="comment-badge">💬 他のレビュー (${othersCount}件)</div>`;
                    }
                    
                    // 平均評点の算出
                    const ratings = item.ratings || [];
                    const totalScores = ratings.map(r => r.total_score).filter(s => s !== undefined && s !== null);
                    let ratingBadgeHtml = '';
                    if (totalScores.length > 0) {
                        const avg = (totalScores.reduce((a,b)=>a+b, 0) / totalScores.length).toFixed(1);
                        ratingBadgeHtml = `<div class="card-rating-badge">★ ${avg} (${totalScores.length})</div>`;
                    }
                    
                    // マイ評価の算出
                    const myRating = ratings.find(r => r.user_name === 'hitocie');
                    let myRatingBadgeHtml = '';
                    if (myRating && myRating.total_score !== undefined && myRating.total_score !== null) {
                        myRatingBadgeHtml = `<div class="card-my-rating-badge">あなた: ★ ${myRating.total_score.toFixed(1)}</div>`;
                    }
                    
                    card.innerHTML = `
                        <div class="sake-id">ID: ${String(item.id).padStart(4, '0')}</div>
                        <div class="image-container">
                            ${myRatingBadgeHtml}
                            ${ratingBadgeHtml}
                            <img src="${item.cropped_image_path_front || NO_IMAGE_PLACEHOLDER}" alt="${item.name}">
                        </div>
                        <div class="sake-info">
                            <div class="sake-brewery">${item.brewery || '不明'}</div>
                            <div class="sake-name">${item.name}</div>
                            <div style="margin-bottom: 0.5rem; height: 1.5rem;">${indicatorHtml}</div>
                            <div class="tag-container">
                                <span class="tag">${item.alcohol_content ? item.alcohol_content + '度' : '度数不明'}</span>
                                <span class="tag tag-type">${item.sake_type || '特定名称不明'}</span>
                            </div>
                        </div>
                        <div class="card-actions">
                            <button class="action-btn btn-edit" onclick="event.stopPropagation(); openEditModal(${item.id})">${editBtnText}</button>
                            <button class="action-btn btn-others" onclick="event.stopPropagation(); openOthersModal(${item.id})">🔍 他のコメント</button>
                        </div>
                    `;
                    
                    card.addEventListener('click', () => showDetailModal(item));
                    grid.appendChild(card);
                });
            }

            // A. 詳細スペック表示 (すべてのカラム値を表示)
            function showDetailModal(item) {
                currentSake = item;
                showFrontImage = true;
                
                detailImg.src = item.cropped_image_path_front || NO_IMAGE_PLACEHOLDER;
                detailImgLabel.textContent = '表面';
                
                if (item.cropped_image_path_back) {
                    detailImgToggle.style.display = 'block';
                    detailImgToggle.textContent = '裏面画像を表示';
                } else {
                    detailImgToggle.style.display = 'none';
                }
                
                document.getElementById('detailName').textContent = item.name;
                document.getElementById('detailSubName').textContent = item.sub_name || '';
                document.getElementById('detBrewery').textContent = item.brewery || '-';
                document.getElementById('detType').textContent = item.sake_type || '-';
                document.getElementById('detAlcohol').textContent = item.alcohol_content ? `${item.alcohol_content}度` : '-';
                document.getElementById('detPolishing').textContent = item.polishing_rate || '-';
                document.getElementById('detMaterials').textContent = item.raw_materials || '-';
                document.getElementById('detVariety').textContent = item.rice_variety || '非公開';
                document.getElementById('detYeast').textContent = item.yeast || '非公開';
                document.getElementById('detSmv').textContent = item.smv || '非公開';
                document.getElementById('detAcidity').textContent = item.acidity || '非公開';
                document.getElementById('detAminoAcidity').textContent = item.amino_acidity || '非公開';
                document.getElementById('detAddress').textContent = item.brewery_address || '-';
                
                document.getElementById('detComment').textContent = item.comment || '-';
                
                renderTasteMap(item);
                
                openModal('detailModal');
            }

            // 味わいマップの描画ロジック
            function renderTasteMap(item) {
                mapUserDots.innerHTML = '';
                
                const bodyVal = { "濃醇": 1.0, "中間": 0.0, "淡麗辛口": -1.0 };
                const aromaVal = { "華やかフルーティ": 1.0, "しっかり個性的": 0.0, "すっきりおだやか": -1.0 };
                
                const ratings = item.ratings || [];
                let totalX = 0;
                let totalY = 0;
                let validCount = 0;
                
                ratings.forEach(r => {
                    const x = aromaVal[r.aroma_level];
                    const y = bodyVal[r.body_level];
                    
                    if (x !== undefined && y !== undefined) {
                        totalX += x;
                        totalY += y;
                        validCount++;
                        
                        const dot = document.createElement('div');
                        dot.className = 'map-dot-user';
                        
                        const leftPercent = (x + 1) / 2 * 100;
                        const bottomPercent = (y + 1) / 2 * 100;
                        
                        dot.style.left = `${leftPercent}%`;
                        dot.style.bottom = `${bottomPercent}%`;
                        dot.title = `${r.user_name}: ${r.aroma_level} / ${r.body_level}`;
                        mapUserDots.appendChild(dot);
                    }
                });
                
                const defaultX = aromaVal[item.aroma_level];
                const defaultY = bodyVal[item.body_level];
                if (defaultX !== undefined && defaultY !== undefined) {
                    totalX += defaultX;
                    totalY += defaultY;
                    validCount++;
                }
                
                if (validCount > 0) {
                    const avgX = totalX / validCount;
                    const avgY = totalY / validCount;
                    
                    const leftPercent = (avgX + 1) / 2 * 100;
                    const bottomPercent = (avgY + 1) / 2 * 100;
                    
                    mapPinAvg.style.left = `${leftPercent}%`;
                    mapPinAvg.style.bottom = `${bottomPercent}%`;
                    mapPinAvg.style.display = 'block';
                    mapPinAvg.title = `平均評価: (${avgX.toFixed(2)}, ${avgY.toFixed(2)})`;
                } else {
                    mapPinAvg.style.left = '50%';
                    mapPinAvg.style.bottom = '50%';
                    mapPinAvg.title = '評価データがまだありません';
                }
            }

            // B. コメント追加・修正モーダルを開く
            window.openEditModal = function(productId) {
                const item = sakeData.find(d => d.id === productId);
                if (!item) return;
                
                editProductId.value = item.id;
                editImageInput.value = "";
                attachedImageBase64 = "";
                editImagePreviewContainer.style.display = 'none';
                editImagePreviewImg.src = "";
                
                const myRating = item.ratings ? item.ratings.find(r => r.user_name === 'hitocie') : null;
                
                selectedSsiType = "";
                editSsiGroup.querySelectorAll('.ssi-btn').forEach(btn => btn.classList.remove('active'));
                
                // 全員の平均評点と件数を計算
                const ratings = item.ratings || [];
                const totalScores = ratings.map(r => r.total_score).filter(s => s !== undefined && s !== null);
                const tasteScores = ratings.map(r => r.taste_score).filter(s => s !== undefined && s !== null);
                const aromaScores = ratings.map(r => r.aroma_score).filter(s => s !== undefined && s !== null);
                
                const avgTotal = totalScores.length > 0 ? (totalScores.reduce((a,b)=>a+b, 0) / totalScores.length).toFixed(1) : null;
                const avgTaste = tasteScores.length > 0 ? (tasteScores.reduce((a,b)=>a+b, 0) / tasteScores.length).toFixed(1) : null;
                const avgAroma = aromaScores.length > 0 ? (aromaScores.reduce((a,b)=>a+b, 0) / aromaScores.length).toFixed(1) : null;
                
                document.getElementById('avgTotalScore').textContent = avgTotal ? `全員の平均: ★${avgTotal} (${totalScores.length}件)` : '全員の平均: なし';
                document.getElementById('avgTasteScore').textContent = avgTaste ? `全員の平均: ★${avgTaste} (${tasteScores.length}件)` : '全員の平均: なし';
                document.getElementById('avgAromaScore').textContent = avgAroma ? `全員の平均: ★${avgAroma} (${aromaScores.length}件)` : '全員の平均: なし';

                if (myRating) {
                    editTitle.textContent = `コメントを修正・削除する - ${item.name}`;
                    editBodyLevel.value = myRating.body_level || "";
                    editAromaLevel.value = myRating.aroma_level || "";
                    editComment.value = myRating.comment || "";
                    editTotalScore.value = myRating.total_score !== undefined && myRating.total_score !== null ? myRating.total_score : "4.0";
                    
                    if (myRating.taste_score !== undefined && myRating.taste_score !== null) {
                        editTasteScore.value = myRating.taste_score;
                        noTasteScore.checked = false;
                    } else {
                        editTasteScore.value = avgTaste || "4.0";
                        noTasteScore.checked = true;
                    }
                    
                    if (myRating.aroma_score !== undefined && myRating.aroma_score !== null) {
                        editAromaScore.value = myRating.aroma_score;
                        noAromaScore.checked = false;
                    } else {
                        editAromaScore.value = avgAroma || "4.0";
                        noAromaScore.checked = true;
                    }
                    
                    if (myRating.ssi_type) {
                        selectedSsiType = myRating.ssi_type;
                        const targetBtn = editSsiGroup.querySelector(`[data-type="${myRating.ssi_type}"]`);
                        if (targetBtn) targetBtn.classList.add('active');
                    }
                    
                    if (myRating.rating_image) {
                        attachedImageBase64 = myRating.rating_image;
                        editImagePreviewImg.src = myRating.rating_image;
                        editImagePreviewContainer.style.display = 'block';
                    }
                    
                    editSubmitBtn.textContent = '更新する';
                    editDeleteBtn.style.display = 'block';
                } else {
                    editTitle.textContent = `コメントを追加する - ${item.name}`;
                    editBodyLevel.value = "";
                    editAromaLevel.value = "";
                    editComment.value = "";
                    editTotalScore.value = avgTotal || "4.0";
                    editTasteScore.value = avgTaste || "4.0";
                    editAromaScore.value = avgAroma || "4.0";
                    noTasteScore.checked = true;
                    noAromaScore.checked = true;
                    
                    editSubmitBtn.textContent = '登録する';
                    editDeleteBtn.style.display = 'none';
                }
                
                // イベントを発火させてUI表示値を同期
                noTasteScore.dispatchEvent(new Event('change'));
                noAromaScore.dispatchEvent(new Event('change'));
                editTotalScore.dispatchEvent(new Event('input'));
                
                openModal('editModal');
            };

            // D. スペック手動編集モーダルを開く
            function openSpecsEditModal() {
                if (!currentSake) return;
                
                specsEditId.value = currentSake.id;
                specsEditCategory.value = currentSake.sake_type || "";
                specsEditAlcohol.value = currentSake.alcohol_content || "";
                specsEditPolish.value = currentSake.polishing_rate || "";
                specsEditIngredients.value = currentSake.raw_materials || "";
                specsEditVariety.value = currentSake.rice_variety || "";
                specsEditYeast.value = currentSake.yeast || "";
                specsEditSmv.value = currentSake.smv || "";
                specsEditAcidity.value = currentSake.acidity || "";
                specsEditAmino.value = currentSake.amino_acidity || "";
                
                // 画像状態のリセット
                specsFrontImageInput.value = "";
                specsBackImageInput.value = "";
                specsFrontImageBase64 = null;
                specsBackImageBase64 = null;
                
                if (currentSake.cropped_image_path_front) {
                    specsFrontPreviewImg.src = currentSake.cropped_image_path_front;
                    specsFrontPreviewContainer.style.display = 'block';
                } else {
                    specsFrontPreviewContainer.style.display = 'none';
                }
                
                if (currentSake.cropped_image_path_back) {
                    specsBackPreviewImg.src = currentSake.cropped_image_path_back;
                    specsBackPreviewContainer.style.display = 'block';
                } else {
                    specsBackPreviewContainer.style.display = 'none';
                }
                
                hideModal('detailModal');
                openModal('specsEditModal');
            }

            // C. 他者のコメント参照モーダルを開く
            window.openOthersModal = function(productId) {
                const item = sakeData.find(d => d.id === productId);
                if (!item) return;
                
                othersTitle.textContent = `他のユーザーのレビュー - ${item.name}`;
                othersTimeline.innerHTML = '';
                
                const othersRatings = item.ratings ? item.ratings.filter(r => r.user_name !== 'hitocie') : [];
                
                if (othersRatings.length > 0) {
                    othersRatings.forEach(r => {
                        const dateStr = r.created_at ? r.created_at.split('T')[0] : '不明';
                        
                        let tagsHtml = '';
                        if (r.ssi_type) tagsHtml += `<span class="comment-tag-small">${r.ssi_type}</span>`;
                        if (r.body_level) tagsHtml += `<span class="comment-tag-small">${r.body_level}</span>`;
                        if (r.aroma_level) tagsHtml += `<span class="comment-tag-small">${r.aroma_level}</span>`;
                        
                        // 個別評点があればタグで表示
                        if (r.taste_score !== undefined && r.taste_score !== null) tagsHtml += `<span class="comment-tag-small" style="color: var(--success);">味: ★${r.taste_score.toFixed(1)}</span>`;
                        if (r.aroma_score !== undefined && r.aroma_score !== null) tagsHtml += `<span class="comment-tag-small" style="color: var(--accent);">香: ★${r.aroma_score.toFixed(1)}</span>`;
                        
                        let imgHtml = '';
                        if (r.rating_image) {
                            imgHtml = `<br><img class="comment-photo" src="${r.rating_image}" onclick="window.open('${r.rating_image}')" alt="口コミ添付画像">`;
                        }
                        
                        const starHtml = r.total_score !== undefined && r.total_score !== null ? getStarHtml(r.total_score) : '';
                        
                        const itemDiv = document.createElement('div');
                        itemDiv.className = 'comment-item';
                        itemDiv.innerHTML = `
                            <div class="comment-header">
                                <span class="comment-user">👤 ${r.user_name}</span>
                                <span class="comment-date">${starHtml} ${dateStr}</span>
                            </div>
                            <div class="comment-tags">
                                ${tagsHtml}
                            </div>
                            <div class="comment-body">
                                ${r.comment}
                                ${imgHtml}
                            </div>
                        `;
                        othersTimeline.appendChild(itemDiv);
                    });
                } else {
                    othersTimeline.innerHTML = '<div style="text-align: center; color: var(--text-muted); font-size: 0.85rem; padding: 2rem 0;">他の方のレビューコメントはまだありません。</div>';
                }
                
                openModal('othersModal');
            };

            // 詳細モーダル画像切り替え
            function toggleDetailImage() {
                if (!currentSake) return;
                showFrontImage = !showFrontImage;
                if (showFrontImage) {
                    detailImg.src = currentSake.cropped_image_path_front || NO_IMAGE_PLACEHOLDER;
                    detailImgLabel.textContent = '表面';
                    detailImgToggle.textContent = '裏面画像を表示';
                } else {
                    detailImg.src = currentSake.cropped_image_path_back || NO_IMAGE_PLACEHOLDER;
                    detailImgLabel.textContent = '裏面';
                    detailImgToggle.textContent = '表面画像を表示';
                }
            }

            // フィルター酒蔵/特定名称設定
            function setupFilters() {
                const breweries = new Set();
                const types = new Set();
                sakeData.forEach(item => {
                    if (item.brewery) breweries.add(item.brewery);
                    if (item.sake_type) types.add(item.sake_type);
                });
                
                const sortedBreweries = Array.from(breweries).sort((a, b) => a.localeCompare(b, 'ja'));
                const sortedTypes = Array.from(types).sort((a, b) => a.localeCompare(b, 'ja'));

                sortedBreweries.forEach(b => {
                    const opt = document.createElement('option');
                    opt.value = b; opt.textContent = b;
                    breweryFilter.appendChild(opt);
                });
                sortedTypes.forEach(t => {
                    const opt = document.createElement('option');
                    opt.value = t; opt.textContent = t;
                    typeFilter.appendChild(opt);
                });
            }

            // モーダルユーティリティ
            function openModal(id) {
                const m = document.getElementById(id);
                m.classList.add('active');
                document.body.style.overflow = 'hidden';
            }
            window.hideModal = function(id) {
                const m = document.getElementById(id);
                m.classList.remove('active');
                document.body.style.overflow = '';
            };

            init();
        });
    