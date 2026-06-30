// voucher_cua_toi.js
document.addEventListener('DOMContentLoaded', function() {
    // Cập nhật số lượng voucher trong menu
    function updateVoucherCount() {
        const countEl = document.getElementById('voucher-count');
        if (!countEl) return;

        fetch('/voucher-count/')  // Bạn có thể tạo view API sau
            .then(res => res.json())
            .then(data => {
                countEl.textContent = data.count || 0;
                if (data.count > 0) {
                    countEl.style.display = 'inline-block';
                }
            })
            .catch(() => {});
    }

    if (document.getElementById('voucher-count')) {
        updateVoucherCount();
    }

    // Animation khi click vào voucher
    const voucherLinks = document.querySelectorAll('.voucher-menu-item');
    voucherLinks.forEach(link => {
        link.addEventListener('click', function() {
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 200);
        });
    });
});