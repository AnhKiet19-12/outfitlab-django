// ====================== XÁC NHẬN ĐÃ NHẬN HÀNG ======================

function xacNhanNhanHang(donId) {
    Swal.fire({
        title: 'Xác nhận đã nhận hàng?',
        html: 'Bạn chắc chắn đã nhận được toàn bộ hàng hóa?<br><small class="text-muted">Đơn hàng sẽ chuyển sang Lịch sử sau khi xác nhận.</small>',
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#10b981',
        cancelButtonColor: '#6b7280',
        confirmButtonText: 'Đã nhận hàng',
        cancelButtonText: 'Hủy'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/don-hang/xac-nhan-nhan/${donId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        title: '✅ Thành công!',
                        text: 'Đơn hàng đã được chuyển sang Lịch sử đơn hàng.',
                        icon: 'success',
                        timer: 2000,
                        showConfirmButton: false
                    }).then(() => {
                        location.reload(); // Reload để cập nhật danh sách
                    });
                } else {
                    Swal.fire('Lỗi', data.message || 'Không thể xác nhận đơn hàng.', 'error');
                }
            })
            .catch(() => {
                Swal.fire('Lỗi', 'Có lỗi kết nối. Vui lòng thử lại.', 'error');
            });
        }
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