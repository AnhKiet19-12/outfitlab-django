// ====================== LỊCH SỬ HOÀN TIỀN JS ======================

document.addEventListener('DOMContentLoaded', function() {
    console.log('%c✅ Lịch sử hoàn tiền JS loaded!', 'color: #ec4899; font-weight: bold; font-size: 14px');

    // Animation cho các card
    const cards = document.querySelectorAll('.refund-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            card.style.transition = `all 0.5s ease ${index * 0.1}s`;
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 200);
    });

    // Hover effect cho status badge
    const badges = document.querySelectorAll('.status-badge');
    badges.forEach(badge => {
        badge.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.08)';
        });
        badge.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
});