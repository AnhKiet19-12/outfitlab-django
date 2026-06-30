const baseUrl = window.location.pathname;

function applyFilters() {
    const url = new URL(baseUrl, window.location.origin);

    // Giữ nguyên giới tính hiện tại (quan trọng nhất)
    const currentGender = new URLSearchParams(window.location.search).get('gioi_tinh');
    if (currentGender) {
        url.searchParams.set('gioi_tinh', currentGender);
    }

    // danh mục (nếu có)
    document.querySelectorAll('[id^="dm"]').forEach(item => {
        if (item.checked) {
            url.searchParams.append("danh_muc", item.value);
        }
    });

    // giới tính từ tab (ưu tiên)
    let gioiTinh = [];
    ["nam","nu","unisex"].forEach(id => {
        const el = document.getElementById(id);
        if (el && el.checked) gioiTinh.push(id);
    });
    if (gioiTinh.length) {
        url.searchParams.set("gioi_tinh", gioiTinh.join(","));
    }

    // giá
    const minEl = document.getElementById("gia_min");
    const maxEl = document.getElementById("gia_max");
    if (minEl && minEl.value) url.searchParams.set("gia_min", minEl.value);
    if (maxEl && maxEl.value) url.searchParams.set("gia_max", maxEl.value);

    // sort
    const sortEl = document.getElementById("sortSelect");
    const sortValue = sortEl ? sortEl.value : "";
    url.searchParams.set("sort", sortValue);

    // Loading
    const loadingEl = document.getElementById("loading");
    if (loadingEl) loadingEl.classList.remove("d-none");

    fetch(url, {
        headers: { "X-Requested-With": "XMLHttpRequest" }
    })
    .then(res => res.json())
    .then(data => {
        const grid = document.getElementById("productGrid");
        if (!grid) return;

        grid.style.opacity = "0";

        setTimeout(() => {
            grid.innerHTML = data.html;
            animateProducts();
            grid.style.opacity = "1";
        }, 250);

        if (loadingEl) loadingEl.classList.add("d-none");
    })
    .catch(err => {
        console.error("Lỗi filter:", err);
        if (loadingEl) loadingEl.classList.add("d-none");
    });
}

function animateProducts() {
    const items = document.querySelectorAll(".product-item");
    items.forEach((item, index) => {
        item.style.opacity = "0";
        item.style.transform = "translateY(30px)";

        setTimeout(() => {
            item.style.transition = "all .5s ease";
            item.style.opacity = "1";
            item.style.transform = "translateY(0)";
        }, index * 80);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    animateProducts();

    // Sort
    const sortSelect = document.getElementById("sortSelect");
    if (sortSelect) {
        sortSelect.addEventListener("change", applyFilters);
    }

    // Auto filter khác (nếu có)
    document.querySelectorAll(".auto-filter").forEach(el => {
        el.addEventListener("change", applyFilters);
    });

    // Giá Enter
    ["gia_min", "gia_max"].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("keyup", e => {
                if (e.key === "Enter") applyFilters();
            });
        }
    });

    // Debounce giá
    let timeout;
    ["gia_min", "gia_max"].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("input", () => {
                clearTimeout(timeout);
                timeout = setTimeout(applyFilters, 600);
            });
        }
    });
});