document.addEventListener('DOMContentLoaded', function() {
    const slides = document.querySelectorAll('.slide');
    let current = 0;

    function nextSlide() {
        slides[current].classList.remove('active');
        current = (current + 1) % slides.length;
        slides[current].classList.add('active');
    }

    // Khởi tạo slide đầu tiên
    if (slides.length > 0) {
        slides[0].classList.add('active');
        setInterval(nextSlide, 5000);   // chuyển ảnh mỗi 5 giây
    }
});