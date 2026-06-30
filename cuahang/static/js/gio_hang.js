document.addEventListener('DOMContentLoaded', function() {

    const selectAll = document.getElementById('selectAll');
    const itemCheckboxes = document.querySelectorAll('.item-checkbox');

    // ====================== UPDATE TOTAL ======================
    window.updateTotal = function() {
        let subtotal = 0;
        document.querySelectorAll('.cart-item').forEach(item => {
            const checkbox = item.querySelector('.item-checkbox');
            if (checkbox && checkbox.checked) {
                const itemTotalText = item.querySelector('.item-total')?.textContent || '0';
                subtotal += parseFloat(itemTotalText.replace(/[^0-9]/g, '')) || 0;
            }
        });

        // === VOUCHER GIẢM GIÁ ===
        const ggSelect = document.getElementById('voucher_giamgia');
        let discount = 0;
        if (ggSelect) {
            const option = ggSelect.options[ggSelect.selectedIndex];
            if (option && option.dataset.type) {
                const type = option.dataset.type;
                const value = parseInt(option.dataset.value) || 0;
                if (type === 'phan_tram') {
                    discount = Math.floor(subtotal * value / 100);
                } else if (type === 'tien') {
                    discount = value;
                }
            }
        }

        // === VOUCHER FREESHIP ===
        const fsSelect = document.getElementById('voucher_freeship');
        let freeship = false;
        if (fsSelect) {
            const option = fsSelect.options[fsSelect.selectedIndex];
            if (option && option.dataset.type === 'freeship') {
                freeship = true;
            }
        }

        const shipping = freeship ? 0 : 30000;
        const finalTotal = subtotal - discount + shipping;

        // ====================== CẬP NHẬT GIAO DIỆN AN TOÀN ======================
        const tamTinhEl = document.getElementById('tam_tinh');
        if (tamTinhEl) {
            tamTinhEl.textContent = subtotal.toLocaleString('vi-VN') + ' ₫';
        }

        const tongTienFinalEl = document.getElementById('tong_tien_final');
        if (tongTienFinalEl) {
            tongTienFinalEl.textContent = finalTotal.toLocaleString('vi-VN') + ' ₫';
        }

        // Giảm giá
        const giamGiaRow = document.getElementById('giam_gia_row');
        const giamGiaAmount = document.getElementById('giam_gia_amount');
        if (giamGiaRow && giamGiaAmount) {
            giamGiaAmount.textContent = '-' + discount.toLocaleString('vi-VN') + ' ₫';
            giamGiaRow.style.display = discount > 0 ? 'flex' : 'none';
        }

        // Phí ship
        const phiShipEl = document.getElementById('phi_ship_display');
        if (phiShipEl) {
            phiShipEl.textContent = freeship ? '0 ₫ (Freeship)' : '30.000 ₫';
        }
    };

    // Chọn tất cả
    if (selectAll) {
        selectAll.addEventListener('change', function() {
            itemCheckboxes.forEach(cb => cb.checked = this.checked);
            updateTotal();
        });
    }

    // Click từng checkbox
    itemCheckboxes.forEach(cb => {
        cb.addEventListener('change', updateTotal);
    });

    // Tăng / Giảm số lượng
    document.querySelectorAll('.plus-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.parentElement.querySelector('.quantity-input');
            if (!input) return;
            let qty = parseInt(input.value) || 1;
            input.value = qty + 1;
            updateItemTotal(this.closest('.cart-item'));
            updateTotal();
        });
    });

    document.querySelectorAll('.minus-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.parentElement.querySelector('.quantity-input');
            if (!input) return;
            let qty = parseInt(input.value) || 1;
            if (qty > 1) {
                input.value = qty - 1;
                updateItemTotal(this.closest('.cart-item'));
                updateTotal();
            }
        });
    });

    // Xóa sản phẩm
    document.querySelectorAll('.remove-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            if (confirm('Bạn có chắc muốn xóa sản phẩm này khỏi giỏ hàng?')) {
                const cartItem = this.closest('.cart-item');
                if (!cartItem) return;
                
                const itemId = cartItem.dataset.id;
                
                fetch(`/xoa-khoi-gio/${itemId}/`, { 
                    method: 'POST',
                    headers: { 'X-CSRFToken': getCookie('csrftoken') }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        cartItem.remove();
                        updateTotal();
                        if (document.querySelectorAll('.cart-item').length === 0) {
                            location.reload();
                        }
                    } else {
                        alert('Có lỗi khi xóa sản phẩm!');
                    }
                })
                .catch(err => {
                    console.error(err);
                    alert('Có lỗi kết nối!');
                });
            }
        });
    });

    function updateItemTotal(cartItem) {
        if (!cartItem) return;
        const priceEl = cartItem.querySelector('.text-danger');
        if (!priceEl) return;
        
        const price = parseFloat(priceEl.textContent.replace(/[^0-9]/g, '')) || 0;
        const qtyInput = cartItem.querySelector('.quantity-input');
        const qty = parseInt(qtyInput ? qtyInput.value : 1) || 1;
        
        const totalEl = cartItem.querySelector('.item-total');
        if (totalEl) {
            totalEl.textContent = (price * qty).toLocaleString('vi-VN') + ' ₫';
        }
    }

    // Nút thanh toán
    window.thanhToan = function() {
        const selectedCheckboxes = document.querySelectorAll('.item-checkbox:checked');
        const selectedItems = Array.from(selectedCheckboxes).map(cb => cb.dataset.id);

        if (selectedItems.length === 0) {
            alert('Vui lòng chọn ít nhất một sản phẩm để thanh toán!');
            return;
        }

        const params = new URLSearchParams();
        selectedItems.forEach(id => params.append('selected_items', id));
        window.location.href = `/thanh-toan/?${params.toString()}`;
    };

    // Khởi tạo
    updateTotal();
});

// CSRF Token
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