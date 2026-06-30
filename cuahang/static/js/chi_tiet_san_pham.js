let bienTheList = [];
let selectedMauSac = null;
let selectedKichCo = null;
let selectedBienTheId = null;

document.addEventListener('DOMContentLoaded', function() {
    const jsonElement = document.getElementById('bien_the_data');
    if (jsonElement) {
        try {
            bienTheList = JSON.parse(jsonElement.textContent.trim());
        } catch (e) {
            console.error("Lỗi parse JSON:", e);
        }
    }

    renderDefaultImage();
    
    if (bienTheList.length > 0) {
        renderColorOptions();
    }

    const btnPlus = document.getElementById('btn-plus');
    const btnMinus = document.getElementById('btn-minus');
    if (btnPlus) btnPlus.addEventListener('click', () => changeQuantity(1));
    if (btnMinus) btnMinus.addEventListener('click', () => changeQuantity(-1));
});

// ẢNH MẶC ĐỊNH
function renderDefaultImage() {
    const container = document.getElementById('carousel-inner');
    let url = document.getElementById('default-image').value;
    if (url) {
        if (!url.startsWith('/media/') && !url.startsWith('http')) {
            url = `/media/${url}`;
        }
        container.innerHTML = `
            <div class="carousel-item active">
                <img src="${url}" class="d-block w-100 main-product-image" alt="Sản phẩm">
            </div>
        `;
    }
}

// MÀU SẮC & KÍCH CỠ
function renderColorOptions() {
    const container = document.getElementById('color-options');
    if (!container) return;
    container.innerHTML = '';

    const colors = [...new Set(bienTheList.map(bt => bt.mau_sac))];
    colors.forEach(color => {
        const btn = document.createElement('button');
        btn.className = 'color-option btn btn-outline-secondary me-2 mb-2';
        btn.textContent = color;
        btn.addEventListener('click', () => selectColor(color, btn));
        container.appendChild(btn);
    });

    if (colors.length > 0) selectColor(colors[0], container.querySelector('.color-option'));
}

function selectColor(color, btnElement) {
    document.querySelectorAll('.color-option').forEach(b => b.classList.remove('active'));
    if (btnElement) btnElement.classList.add('active');
    
    selectedMauSac = color;
    const variant = bienTheList.find(bt => bt.mau_sac === color);
    
    if (variant && variant.hinh_anh) {
        let url = variant.hinh_anh;
        if (!url.startsWith('/media/') && !url.startsWith('http')) url = `/media/${url}`;
        document.getElementById('carousel-inner').innerHTML = `
            <div class="carousel-item active">
                <img src="${url}" class="d-block w-100 main-product-image" alt="${color}">
            </div>
        `;
    }
    renderSizeOptions(color);
}

function renderSizeOptions(color) {
    const container = document.getElementById('size-options');
    if (!container) return;
    container.innerHTML = '';

    const sizes = bienTheList.filter(bt => bt.mau_sac === color);
    sizes.forEach(item => {
        const btn = document.createElement('button');
        btn.className = 'size-option btn btn-outline-secondary me-2 mb-2';
        btn.textContent = item.kich_co;
        btn.addEventListener('click', () => selectSize(item, btn));
        container.appendChild(btn);
    });

    if (sizes.length > 0) selectSize(sizes[0], container.querySelector('.size-option'));
}

function selectSize(item, btnElement) {
    document.querySelectorAll('.size-option').forEach(b => b.classList.remove('active'));
    if (btnElement) btnElement.classList.add('active');

    selectedKichCo = item.kich_co;
    selectedBienTheId = item.id;

    document.getElementById('gia_hien_thi').textContent = Number(item.gia).toLocaleString('vi-VN') + ' ₫';
    
    const tonKhoEl = document.getElementById('ton_kho');
    tonKhoEl.textContent = `Còn ${item.so_luong} sản phẩm`;
    tonKhoEl.className = item.so_luong > 0 ? 'ms-3 text-success fw-medium' : 'ms-3 text-danger';
}

function changeQuantity(delta) {
    const input = document.getElementById('so_luong');
    if (input) {
        let qty = parseInt(input.value) || 1;
        input.value = Math.max(1, qty + delta);
    }
}

function themVaoGio() {
    if (!selectedBienTheId) {
        alert("Vui lòng chọn màu sắc và kích cỡ!");
        return;
    }
    window.location.href = `/them-gio/${selectedBienTheId}/`;
}

function muaNgay() {
    if (!selectedBienTheId) {
        alert("Vui lòng chọn màu sắc và kích cỡ!");
        return;
    }
    window.location.href = `/mua-ngay/${selectedBienTheId}/`;
}

// Xem ảnh đánh giá lớn
function showReviewImage(imgElement) {
    const modal = new bootstrap.Modal(document.getElementById('reviewImageModal'));
    
    document.getElementById('modalReviewImage').src = imgElement.src;
    document.getElementById('reviewerName').textContent = 
        imgElement.closest('.review-card').querySelector('strong').textContent;
    
    const stars = imgElement.closest('.review-card').querySelector('.star-rating').innerHTML;
    document.getElementById('modalReviewStars').innerHTML = stars;
    
    const content = imgElement.closest('.review-card').querySelector('p').textContent;
    document.getElementById('modalReviewContent').textContent = content;

    modal.show();
}