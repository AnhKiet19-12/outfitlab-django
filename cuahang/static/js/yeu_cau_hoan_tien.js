// ====================== YÊU CẦU HOÀN TIỀN JS ======================

document.addEventListener('DOMContentLoaded', function() {
    console.log('%c✅ Yêu cầu hoàn tiền JS loaded!', 'color: #ec4899; font-weight: bold');

    const fileInput = document.getElementById('id_hinh_anh');
    const previewContainer = document.getElementById('preview-container');

    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewContainer.innerHTML = `
                        <img src="${e.target.result}" class="preview-image img-fluid" alt="Preview">
                    `;
                }
                reader.readAsDataURL(file);
            }
        });
    }
});

// Animation cho form khi load
window.onload = function() {
    const form = document.querySelector('.form-container');
    if (form) {
        form.style.opacity = '0';
        setTimeout(() => {
            form.style.transition = 'all 0.6s ease';
            form.style.opacity = '1';
        }, 100);
    }
};