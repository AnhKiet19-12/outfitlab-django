// ====================== MODAL XÁC NHẬN ĐẸP ======================

function showConfirmModal(donId) {
    const modalHTML = `
        <div class="custom-modal" id="confirmModal">
            <div class="modal-content">
                <div class="modal-header">
                    <i class="fas fa-truck modal-icon"></i>
                    <h3>Xác nhận nhận hàng</h3>
                </div>
                <div class="modal-body">
                    <p><strong>Bạn chắc chắn đã nhận được hàng thành công?</strong></p>
                    <small class="text-muted">Đơn hàng sẽ được chuyển sang Lịch sử đơn hàng.</small>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary px-4" onclick="closeModal()">Hủy</button>
                    <button class="btn btn-success px-4" onclick="confirmReceive(${donId})">
                        <i class="fas fa-check"></i> Đã nhận được hàng
                    </button>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    setTimeout(() => {
        document.getElementById('confirmModal').classList.add('show');
    }, 50);
}

function closeModal() {
    const modal = document.getElementById('confirmModal');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => modal.remove(), 300);
    }
}

function confirmReceive(donId) {
    closeModal();

    fetch(`/don-hang/xac-nhan-nhan/${donId}/`, {
        method: 'POST',
        headers: { 
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const card = document.getElementById(`order-${donId}`);
            if (card) {
                card.style.transition = 'all 0.5s ease';
                card.style.opacity = '0';
                card.style.transform = 'translateY(30px)';
                setTimeout(() => card.remove(), 500);
            }
            showSuccessModal();
        } else {
            alert('❌ ' + (data.error || 'Có lỗi xảy ra'));
        }
    })
    .catch(() => alert('❌ Lỗi kết nối. Vui lòng thử lại.'));
}

function showSuccessModal() {
    const successHTML = `
        <div class="custom-modal" id="successModal">
            <div class="modal-content">
                <div class="modal-header success-header">
                    <i class="fas fa-check-circle modal-icon"></i>
                    <h3>Cảm ơn bạn!</h3>
                </div>
                <div class="modal-body">
                    <p>Đơn hàng đã được chuyển sang <strong>Lịch sử đơn hàng</strong> thành công.</p>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary px-5" onclick="closeSuccessModal()">OK</button>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', successHTML);
    setTimeout(() => {
        document.getElementById('successModal').classList.add('show');
    }, 50);
}

function closeSuccessModal() {
    const modal = document.getElementById('successModal');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => modal.remove(), 300);
    }
}

// Gọi khi click nút
function xacNhanNhanHang(donId) {
    showConfirmModal(donId);
}

// CSRF Helper
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