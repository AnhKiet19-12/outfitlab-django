// ====================== LỊCH SỬ ĐƠN HÀNG JS ======================

let currentDonId = null;
let currentSanPhamId = null;
let currentTenSanPham = '';

// Mở modal yêu cầu hoàn tiền
function yeuCauHoanTien(donId, sanPhamId, tenSanPham) {
    currentDonId = donId;
    currentSanPhamId = sanPhamId;
    currentTenSanPham = tenSanPham || 'Sản phẩm';

    // Hiển thị thông tin sản phẩm
    document.getElementById('modal-product-info').innerHTML = `
        <div class="d-flex align-items-center gap-3">
            <strong class="text-pink">Đơn hàng #${donId}</strong>
            <span class="badge bg-light text-dark">${tenSanPham}</span>
        </div>
    `;

    // Reset form
    document.getElementById('lyDo').value = '';
    document.getElementById('moTa').value = '';
    document.getElementById('hinhAnh').value = '';

    // Hiển thị modal
    const modal = new bootstrap.Modal(document.getElementById('hoanTienModal'));
    modal.show();
}

// Gửi yêu cầu hoàn tiền qua AJAX (hỗ trợ upload ảnh)
function guiYeuCauHoanTien() {
    const lyDo = document.getElementById('lyDo').value;
    const moTa = document.getElementById('moTa').value.trim();
    const hinhAnhFile = document.getElementById('hinhAnh').files[0];

    if (!lyDo) {
        Swal.fire({
            title: 'Chưa chọn lý do!',
            text: 'Vui lòng chọn lý do hoàn tiền / trả hàng',
            icon: 'warning',
            confirmButtonColor: '#ec4899'
        });
        return;
    }

    const formData = new FormData();
    formData.append('ly_do', lyDo);
    formData.append('mo_ta', moTa);
    if (hinhAnhFile) {
        formData.append('hinh_anh', hinhAnhFile);
    }

    const modal = bootstrap.Modal.getInstance(document.getElementById('hoanTienModal'));
    modal.hide();

    fetch(`/yeu-cau-hoan-tien/${currentDonId}/${currentSanPhamId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(async response => {
        const text = await response.text();

        try {
            return JSON.parse(text);
        } catch (e) {
            console.error('Response không phải JSON:', text);
            throw new Error('Server trả về HTML thay vì JSON');
        }
    })
    .then(data => {
        if (data.success) {
            Swal.fire({
                title: '✅ Yêu cầu đã được gửi thành công!',
                html: `Đơn hàng <strong>#${currentDonId}</strong><br>
                       Sản phẩm: <strong>${currentTenSanPham}</strong><br><br>
                       Chúng tôi sẽ kiểm tra và liên hệ với bạn sớm nhất.`,
                icon: 'success',
                confirmButtonText: 'Đóng',
                confirmButtonColor: '#ec4899'
            }).then(() => {
                location.reload();
            });
        } else {
            Swal.fire({
                title: '❌ Có lỗi xảy ra',
                text: JSON.stringify(data.error),
                icon: 'error',
                confirmButtonColor: '#ec4899'
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);

        Swal.fire({
            title: '❌ Lỗi',
            text: error.message,
            icon: 'error',
            confirmButtonColor: '#ec4899'
        });
    });
}

// Hàm lấy CSRF Token
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

// Khởi tạo khi trang load
document.addEventListener('DOMContentLoaded', function() {
    console.log('%c✅ Lịch sử đơn hàng JS (AJAX + Upload) loaded!', 'color: #ec4899; font-weight: bold; font-size: 14px');
});