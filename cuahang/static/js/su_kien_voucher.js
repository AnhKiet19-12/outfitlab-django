// su_kien_voucher.js
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.voucher-card');
    
    cards.forEach((card, index) => {
        // Delay animation
        card.style.animationDelay = `${index * 0.1}s`;
        
        // Click effect
        card.addEventListener('click', function(e) {
            if (e.target.tagName === 'A') return;
            
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 200);
        });
    });

    // Confetti effect khi hover một số card
    function createConfetti() {
        const colors = ['#ec4899', '#0ea5e9', '#fbbf24'];
        for (let i = 0; i < 30; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.left = Math.random() * 100 + 'vw';
            confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.animationDuration = Math.random() * 3 + 2 + 's';
            confetti.style.opacity = Math.random() + 0.5;
            document.body.appendChild(confetti);
            
            setTimeout(() => confetti.remove(), 5000);
        }
    }

    // Thêm hiệu ứng confetti khi hover card
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            if (Math.random() > 0.7) { // Random confetti
                createConfetti();
            }
        });
    });
});