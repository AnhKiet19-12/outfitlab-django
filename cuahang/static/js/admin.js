// ====================== ADMIN OUTFITLAB - JAVASCRIPT ======================

document.addEventListener('DOMContentLoaded', function() {

    // Hover effect cho table rows
    const rows = document.querySelectorAll('tr');
    rows.forEach(row => {
        row.addEventListener('mouseenter', () => {
            row.style.transition = 'all 0.3s ease';
        });
    });

    // Animation cho badge
    const badges = document.querySelectorAll('.badge');
    badges.forEach((badge, index) => {
        badge.style.animationDelay = `${index * 50}ms`;
        badge.classList.add('animate__animated', 'animate__fadeIn');
    });

    // Confirm khi xóa
    const deleteLinks = document.querySelectorAll('a[href*="delete"]');
    deleteLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!confirm('❗ Bạn có chắc chắn muốn xóa mục này không?')) {
                e.preventDefault();
            }
        });
    });

    // Thêm class active cho sidebar
    const currentUrl = window.location.href;
    const sidebarLinks = document.querySelectorAll('.sidebar a');
    sidebarLinks.forEach(link => {
        if (currentUrl.includes(link.getAttribute('href'))) {
            link.style.backgroundColor = 'rgba(236, 72, 153, 0.1)';
            link.style.borderLeft = '4px solid #ec4899';
        }
    });

    // Search input animation
    const searchInput = document.querySelector('input[type="search"]');
    if (searchInput) {
        searchInput.addEventListener('focus', () => {
            searchInput.style.boxShadow = '0 0 0 4px rgba(14, 165, 233, 0.3)';
        });
        searchInput.addEventListener('blur', () => {
            searchInput.style.boxShadow = 'none';
        });
    }

    console.log('%c✅ OutfitLab Admin JS Loaded Successfully!', 'color: #ec4899; font-weight: bold;');
});