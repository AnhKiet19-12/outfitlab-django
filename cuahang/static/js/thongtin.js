// thongtin.js - Quản lý Avatar + Địa chỉ giao hàng
document.addEventListener('DOMContentLoaded', function() {

    // ====================== AVATAR ======================
    const avatarWrapper = document.getElementById('avatarWrapper');
    const avatarMenu = document.getElementById('avatarMenu');
    const avatarImage = document.getElementById('avatarImage');
    const fileInput = document.getElementById('id_avatar');
    const deleteInput = document.getElementById('delete_avatar');
    const btnDelete = document.getElementById('btnDeleteAvatar');

    avatarWrapper.addEventListener('click', function(e) {
        if (!['id_avatar', 'btnDeleteAvatar'].includes(e.target.id)) {
            avatarMenu.classList.toggle('show');
        }
    });

    document.addEventListener('click', function(e) {
        if (!avatarWrapper.contains(e.target)) {
            avatarMenu.classList.remove('show');
        }
    });

    document.querySelector('label[for="id_avatar"]').addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = e => avatarImage.src = e.target.result;
            reader.readAsDataURL(this.files[0]);
            deleteInput.value = 'false';
            avatarMenu.classList.remove('show');
        }
    });

    btnDelete.addEventListener('click', function(e) {
        e.preventDefault();
        if (confirm('Bạn có chắc muốn xóa avatar hiện tại?')) {
            avatarImage.src = defaultAvatarUrl;
            deleteInput.value = 'true';
            fileInput.value = '';
            avatarMenu.classList.remove('show');
        }
    });

    // ====================== ĐỊA CHỈ GIAO HÀNG ======================
    const addressModal = new bootstrap.Modal(document.getElementById('addressModal'));
    const addressForm = document.getElementById('addressForm');
    const modalTitle = document.getElementById('modalTitle');
    let currentEditId = null;

    // Mở modal thêm địa chỉ
    document.getElementById('btnAddAddress').addEventListener('click', function() {
        currentEditId = null;
        modalTitle.textContent = 'Thêm địa chỉ mới';
        addressForm.reset();
        document.getElementById('is_default').checked = false;
        addressModal.show();
    });

    // Sửa địa chỉ
    document.querySelectorAll('.edit-address').forEach(btn => {
        btn.addEventListener('click', function() {
            const addressItem = this.closest('.address-item');
            currentEditId = addressItem.dataset.id;

            modalTitle.textContent = 'Sửa địa chỉ';
            
            document.getElementById('ho_ten').value = addressItem.querySelector('strong').textContent.trim();
            document.getElementById('so_dien_thoai').value = addressItem.querySelector('.text-muted').textContent.trim();
            document.getElementById('dia_chi').value = addressItem.querySelector('span:last-child').textContent.trim();
            
            const isDefault = addressItem.querySelector('.badge') !== null;
            document.getElementById('is_default').checked = isDefault;

            addressModal.show();
        });
    });

    // Xóa địa chỉ
    document.querySelectorAll('.delete-address').forEach(btn => {
        btn.addEventListener('click', function() {
            if (!confirm('Bạn có chắc chắn muốn xóa địa chỉ này?')) return;

            const addressItem = this.closest('.address-item');
            const addressId = addressItem.dataset.id;

            fetch(`/xoa-dia-chi/${addressId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addressItem.remove();
                    if (document.querySelectorAll('.address-item').length === 0) {
                        document.getElementById('address-list').innerHTML = 
                            '<p class="text-muted">Bạn chưa có địa chỉ giao hàng nào.</p>';
                    }
                }
            });
        });
    });

    // Lưu địa chỉ (Thêm / Sửa)
    document.getElementById('saveAddressBtn').addEventListener('click', function() {
        const formData = new FormData(addressForm);
        const url = currentEditId ? `/sua-dia-chi/${currentEditId}/` : '/them-dia-chi/';

        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();   // Tải lại trang để cập nhật danh sách
            } else {
                alert(data.message || 'Có lỗi xảy ra');
            }
        })
        .catch(err => console.error(err));
    });

    // ====================== HELPER ======================
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

    console.log('%cTrang Thông tin cá nhân đã sẵn sàng với quản lý địa chỉ!', 'color: #ec4899; font-weight: bold;');
});