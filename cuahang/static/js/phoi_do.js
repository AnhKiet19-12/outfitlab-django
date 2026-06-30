document.addEventListener('DOMContentLoaded', function() {
    const btnGenerate = document.getElementById('btn-generate');
    const resultCard = document.getElementById('outfit-result');
    const loading = document.getElementById('loading-state');
    const addAllBtn = document.getElementById('add-all-to-cart');

    btnGenerate.addEventListener('click', async () => {
        let chieu_cao_str = document.getElementById('chieu_cao').value.trim().replace(',', '.');
        let can_nang_str = document.getElementById('can_nang').value.trim().replace(',', '.');

        const chieu_cao = parseFloat(chieu_cao_str);
        const can_nang = parseFloat(can_nang_str);

        const gioi_tinh = document.getElementById('gioi_tinh').value;
        const dang_nguoi = document.getElementById('dang_nguoi').value;
        const mau_da = document.getElementById('mau_da').value;
        const dip = document.getElementById('dip').value;
        const phong_cach = document.getElementById('phong_cach').value || 'casual';

        if (isNaN(chieu_cao) || isNaN(can_nang) || chieu_cao <= 0 || can_nang <= 0) {
            Swal.fire('Thiếu thông tin', 'Vui lòng nhập chiều cao và cân nặng hợp lệ!', 'warning');
            return;
        }

        resultCard.style.display = 'none';
        loading.style.display = 'block';

        try {
            const response = await fetch('/phoi-do/ai/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    chieu_cao: chieu_cao,
                    can_nang: can_nang,
                    gioi_tinh: gioi_tinh,
                    dang_nguoi: dang_nguoi,
                    mau_da: mau_da,
                    dip: dip,
                    phong_cach: phong_cach
                })
            });

            const data = await response.json();

            if (data.success) {
                renderOutfit(data);
            } else {
                Swal.fire('Lỗi', data.error || 'Không thể tạo outfit!', 'error');
            }
        } catch (e) {
            console.error(e);
            Swal.fire('Lỗi', 'Không thể kết nối với Outfit AI!', 'error');
        } finally {
            loading.style.display = 'none';
        }
    });

    function renderOutfit(data) {
        resultCard.style.display = 'block';

        // === PHẦN MÔ TẢ & LỜI KHUYÊN ===
        let adviceHTML = `
            <div class="alert alert-info">
                <h6><i class="fas fa-lightbulb"></i> Outfit AI gợi ý cho bạn</h6>
                <p class="mb-3">${data.description || 'Outfit phù hợp với body và phong cách của bạn.'}</p>
        `;

        if (data.color_harmony) {
            adviceHTML += `<p><strong>🎨 Phối màu:</strong> ${data.color_harmony}</p>`;
        }
        if (data.trend) {
            adviceHTML += `<p><strong>🔥 Xu hướng:</strong> ${data.trend}</p>`;
        }
        if (data.tips) {
            adviceHTML += `<p><strong>💡 Mẹo phối đồ:</strong> ${data.tips}</p>`;
        }
        adviceHTML += `</div>`;

        document.getElementById('style-advice').innerHTML = adviceHTML;

        // === CÁC MÓN TRONG OUTFIT - NHÓM THEO LOẠI ===
        const itemsByCategory = {
            'ao': [],
            'quan': [],
            'giay': [],
            'phu_kien': []
        };

        if (data.items && data.items.length > 0) {
            data.items.forEach(item => {
                const cat = item.category || 'phu_kien';
                if (itemsByCategory[cat]) {
                    itemsByCategory[cat].push(item);
                } else {
                    itemsByCategory['phu_kien'].push(item);
                }
            });
        }

        let itemsHtml = '';

        const categoryLabels = {
            'ao': '👕 Áo',
            'quan': '👖 Quần',
            'giay': '👟 Giày',
            'phu_kien': '👜 Phụ kiện'
        };

        Object.keys(itemsByCategory).forEach(cat => {
            if (itemsByCategory[cat].length > 0) {
                itemsHtml += `
                    <div class="mb-4">
                        <h6 class="text-pink mb-3">${categoryLabels[cat] || 'Khác'}</h6>
                        <div class="row g-3">
                `;

                itemsByCategory[cat].forEach(item => {
                    itemsHtml += `
                        <div class="col-md-6">
                            <div class="card h-100 border-pink">
                                <div class="card-body">
                                    <h6 class="mb-1">${item.ten}</h6>
                                    <small class="text-muted">${item.ly_do || 'Phù hợp với body và phong cách'}</small>
                                </div>
                            </div>
                        </div>
                    `;
                });

                itemsHtml += `</div></div>`;
            }
        });

        if (!itemsHtml) {
            itemsHtml = `<div class="alert alert-warning">Không có gợi ý chi tiết từ AI.</div>`;
        }

        document.getElementById('ai-items').innerHTML = itemsHtml;

        // === SẢN PHẨM TỪ SHOP ===
        let productsHtml = '';
        if (data.products && data.products.length > 0) {
            data.products.forEach(p => {
                productsHtml += `
                    <div class="col-md-6 col-lg-4">
                        <div class="card product-card h-100">
                            <img src="${p.image}" class="card-img-top" style="height:200px; object-fit:cover;" 
                                 onerror="this.src='/static/images/default-product.jpg'">
                            <div class="card-body">
                                <span class="badge bg-secondary mb-2">${p.category ? p.category.toUpperCase() : ''}</span>
                                <h6 class="mb-1">${p.ten}</h6>
                                <p class="text-pink fw-bold">${p.gia.toLocaleString('vi-VN')} ₫</p>
                                <a href="/san-pham/${p.id}/" class="btn btn-sm btn-outline-primary w-100">Xem chi tiết</a>
                            </div>
                        </div>
                    </div>
                `;
            });
        } else {
            productsHtml = '<p class="text-muted">Không tìm thấy sản phẩm phù hợp trong shop lúc này.</p>';
        }
        document.getElementById('product-list').innerHTML = productsHtml;
    }

    if (addAllBtn) {
        addAllBtn.addEventListener('click', () => {
            Swal.fire({
                title: 'Tính năng đang phát triển',
                text: 'Tính năng thêm toàn bộ outfit vào giỏ hàng sẽ sớm được hoàn thiện!',
                icon: 'info'
            });
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});