document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.payment-option').forEach(option => {
        option.addEventListener('click', function() {
            document.querySelectorAll('.payment-option').forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
        });
    });

    const btnThanhToan = document.getElementById('btnThanhToan');
    if (btnThanhToan) btnThanhToan.addEventListener('click', thucHienThanhToan);

    tinhTienThanhToan();
});

function tinhTienThanhToan() {
    const tamTinhEl = document.getElementById('tam_tinh');
    if (!tamTinhEl) return;

    let subtotal = parseFloat(tamTinhEl.textContent.replace(/[^0-9]/g, '')) || 0;

    const ggSelect = document.getElementById('voucher_giamgia');
    let discount = 0;
    if (ggSelect && ggSelect.value) {
        const option = ggSelect.options[ggSelect.selectedIndex];
        const type = option.dataset.type;
        const value = parseInt(option.dataset.value) || 0;
        if (type === 'phan_tram') discount = Math.floor(subtotal * value / 100);
        else if (type === 'tien') discount = value;
    }

    const fsSelect = document.getElementById('voucher_freeship');
    let freeship = false;
    if (fsSelect && fsSelect.value) freeship = true;

    const phiShip = freeship ? 0 : 30000;
    const tongThanhToan = subtotal - discount + phiShip;

    document.getElementById('giam_gia_amount').textContent = `-${discount.toLocaleString('vi-VN')} ₫`;
    document.getElementById('giam_gia_row').style.display = discount > 0 ? 'flex' : 'none';
    document.getElementById('phi_ship_display').textContent = freeship ? '0 ₫ (Freeship)' : '30.000 ₫';
    document.getElementById('tong_thanh_toan').textContent = tongThanhToan.toLocaleString('vi-VN') + ' ₫';
}

function thucHienThanhToan() {
    const btn = document.getElementById('btnThanhToan');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ĐANG XỬ LÝ...';
    }

    const paymentMethod = document.querySelector('input[name="payment_method"]:checked').value;
    const maGiamGia = document.getElementById('voucher_giamgia').value || '';
    const maFreeship = document.getElementById('voucher_freeship').value || '';

    const formData = new URLSearchParams({
        'payment_method': paymentMethod,
        'ma_giam_gia': maGiamGia,
        'ma_freeship': maFreeship,
        'ho_ten_nhan': document.querySelector('input[name="ho_ten_nhan"]').value,
        'so_dien_thoai_nhan': document.querySelector('input[name="so_dien_thoai_nhan"]').value,
        'dia_chi_giao': document.querySelector('textarea[name="dia_chi_giao"]').value
    });

    fetch(window.location.href, {
        method: 'POST',
        headers: { 
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.method === 'bank') {
            if (data.order_url) window.location.href = data.order_url;
            else alert("Không lấy được link thanh toán!");
        } else if (data.method === 'cod') {
            window.location.href = "/don-hang/";
        } else if (data.error) {
            alert(data.error);
        }
    })
    .catch(err => alert('Có lỗi xảy ra. Vui lòng thử lại!'))
    .finally(() => {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-lock me-2"></i> XÁC NHẬN & THANH TOÁN';
        }
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

// Nút xác nhận đã thanh toán (hiện sau khi quay về từ ZaloPay)
function xacNhanDaThanhToan() {
    if (confirm('Bạn đã hoàn tất thanh toán qua ZaloPay?')) {
        window.location.href = "/don-hang/";
    }
}