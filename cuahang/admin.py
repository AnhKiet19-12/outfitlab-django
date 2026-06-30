from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.http import HttpResponse
from import_export.admin import ImportExportModelAdmin
from django.urls import reverse
from django.utils.safestring import mark_safe

from .resources import SanPhamResource
from django.db.models import Sum

from .models import *


# ====================== THÔNG TIN ADMIN ======================
admin.site.site_header = "OutfitLab - Quản Trị Hệ Thống"
admin.site.site_title = "OutfitLab Admin"
admin.site.index_title = "Trang Quản Trị OutfitLab"


# ====================== NÚT XEM THỐNG KÊ (An toàn) ======================
def get_stats_link():
    return mark_safe('''
        <div style="text-align: center; margin: 20px 0; padding: 15px; background: #1f2937; border-radius: 8px;">
            <a href="/admin-dashboard/" 
               class="btn btn-success btn-lg" 
               style="padding: 12px 30px; font-size: 16px; text-decoration: none;">
                📊 Xem Báo Cáo Thống Kê Chi Tiết
            </a>
        </div>
    ''')


# Ghi đè index an toàn
original_index = admin.site.index

def custom_admin_index(request, extra_context=None):
    extra_context = extra_context or {}
    extra_context['stats_link'] = get_stats_link()
    return original_index(request, extra_context)

admin.site.index = custom_admin_index


# ====================== ADMIN SẢN PHẨM ======================
@admin.register(SanPham)
class SanPhamAdmin(ImportExportModelAdmin):
    resource_class = SanPhamResource
    
    list_display = ('thumbnail', 'ten_san_pham', 'danh_muc', 'loai_san_pham', 
                   'gioi_tinh', 'gia_range', 'ton_kho_status', 'phong_cach')
    list_filter = ('danh_muc', 'loai_san_pham', 'gioi_tinh', 'phong_cach')
    search_fields = ('ten_san_pham', 'mo_ta', 'tags_phoi_do')
    ordering = ('-id',)
    list_per_page = 30

    actions = ['export_selected_to_excel']

    def thumbnail(self, obj):
        if obj.hinh_anh:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover; border-radius:6px;" />', obj.hinh_anh.url)
        return "No Image"
    thumbnail.short_description = 'Ảnh'

    def gia_range(self, obj):
        prices = [bt.gia for bt in obj.bien_the.all()]
        if prices:
            min_p = min(prices)
            max_p = max(prices)
            if min_p == max_p:
                return format_html('<b style="color:#ec4899;">{} ₫</b>', f"{int(min_p):,}".replace(",", "."))
            return format_html('<b style="color:#ec4899;">{} - {} ₫</b>', 
                             f"{int(min_p):,}".replace(",", "."), 
                             f"{int(max_p):,}".replace(",", "."))
        return "Chưa có giá"
    gia_range.short_description = "Giá"

    def ton_kho_status(self, obj):
        total = obj.bien_the.aggregate(Sum('so_luong'))['so_luong__sum'] or 0
        if total == 0:
            return format_html('<span style="color:red; font-weight:bold;">Hết hàng</span>')
        elif total <= 10:
            return format_html('<span style="color:orange; font-weight:bold;">{} cái</span>', total)
        return format_html('<span style="color:green; font-weight:bold;">{} cái</span>', total)
    ton_kho_status.short_description = "Tồn kho"

    def export_selected_to_excel(self, request, queryset):
        resource = self.resource_class()
        dataset = resource.export(queryset)
        response = HttpResponse(
            dataset.export('xlsx'),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="Danh_sach_san_pham.xlsx"'
        return response

    export_selected_to_excel.short_description = "📥 Xuất Excel các sản phẩm đã chọn"

    class BienTheInline(admin.TabularInline):
        model = SanPhamBienThe
        extra = 1
        fields = ('mau_sac', 'kich_co', 'gia', 'so_luong')

    inlines = [BienTheInline]


# ====================== CÁC ADMIN MODEL KHÁC ======================
@admin.register(SanPhamBienThe)
class SanPhamBienTheAdmin(admin.ModelAdmin):
    list_display = ('san_pham', 'mau_sac', 'kich_co', 'gia', 'so_luong', 'trang_thai_ton')
    list_editable = ('gia', 'so_luong')
    list_filter = ('san_pham__danh_muc', 'mau_sac', 'kich_co')
    search_fields = ('san_pham__ten_san_pham',)
    autocomplete_fields = ('san_pham',)
    ordering = ('san_pham', 'mau_sac', 'kich_co')

    def trang_thai_ton(self, obj):
        if obj.so_luong == 0:
            return format_html('<span style="color:red;">Hết hàng</span>')
        elif obj.so_luong <= 5:
            return format_html('<span style="color:orange;">Sắp hết</span>')
        return format_html('<span style="color:green;">Còn hàng</span>')
    trang_thai_ton.short_description = "Trạng thái tồn kho"


@admin.register(DanhGiaSanPham)
class DanhGiaSanPhamAdmin(admin.ModelAdmin):
    list_display = ('san_pham', 'nguoi_dung', 'so_sao_badge', 'ngay_danh_gia')
    list_filter = ('so_sao', 'san_pham')
    search_fields = ('noi_dung', 'nguoi_dung__username')

    def so_sao_badge(self, obj):
        return format_html('<span class="badge bg-warning">⭐ {} sao</span>', obj.so_sao)
    so_sao_badge.short_description = "Đánh giá"


@admin.register(BangSize)
class BangSizeAdmin(admin.ModelAdmin):
    list_display = ('san_pham', 'kich_co', 'chieu_rong', 'chieu_dai_ao', 'chieu_dai_tay')
    list_filter = ('san_pham__loai_san_pham', 'san_pham')
    search_fields = ('san_pham__ten_san_pham',)


@admin.register(DonHang)
class DonHangAdmin(admin.ModelAdmin):
    list_display = ('id', 'nguoi_dung', 'tong_tien_display', 'trang_thai_badge', 'ngay_dat', 'ho_ten_nhan')
    list_filter = ('trang_thai', 'ngay_dat')
    search_fields = ('id', 'nguoi_dung__username', 'ho_ten_nhan')
    ordering = ('-ngay_dat',)
    actions = ['xac_nhan_va_gui_hang']

    def tong_tien_display(self, obj):
        amount = int(obj.tong_tien) if obj.tong_tien else 0
        formatted = f"{amount:,}".replace(",", ".")
        return format_html('<b style="color:#ec4899;">{} ₫</b>', formatted)
    tong_tien_display.short_description = "Tổng tiền"

    def trang_thai_badge(self, obj):
        colors = {
            'cho_xac_nhan': 'bg-warning',
            'da_xac_nhan': 'bg-info',
            'dang_giao': 'bg-primary',
            'da_giao': 'bg-success',
            'da_huy': 'bg-danger',
        }
        return format_html(
            '<span class="badge {} px-3 py-2" style="border-radius:50px; font-weight:600;">{}</span>',
            colors.get(obj.trang_thai, 'bg-secondary'), 
            obj.get_trang_thai_display()
        )
    trang_thai_badge.short_description = "Trạng thái"

    def xac_nhan_va_gui_hang(self, request, queryset):
        updated = queryset.update(trang_thai='da_xac_nhan')
        self.message_user(request, f"✅ Đã xác nhận {updated} đơn hàng thành công!")
    xac_nhan_va_gui_hang.short_description = "✅ Xác nhận & Gửi hàng"


@admin.register(YeuCauHoanTien)
class YeuCauHoanTienAdmin(admin.ModelAdmin):
    list_display = ('id', 'don_hang_link', 'san_pham', 'nguoi_dung', 'trang_thai_badge', 'ngay_yeu_cau')
    list_filter = ('trang_thai', 'ly_do', 'ngay_yeu_cau')
    search_fields = ('don_hang__id', 'san_pham__ten_san_pham', 'mo_ta')
    ordering = ('-ngay_yeu_cau',)
    readonly_fields = ('ngay_yeu_cau', 'ngay_xu_ly')
    actions = ['duyet_hoan_tien', 'tu_choi_yeu_cau']

    def don_hang_link(self, obj):
        return format_html('<a href="/admin/cuahang/donhang/{}/change/">Đơn #{}</a>', obj.don_hang.id, obj.don_hang.id)
    don_hang_link.short_description = "Đơn hàng"

    def trang_thai_badge(self, obj):
        colors = {
            'cho_xu_ly': 'bg-warning',
            'dang_xu_ly': 'bg-info',
            'da_hoan_tien': 'bg-success',
            'da_tu_choi': 'bg-danger',
        }
        return format_html('<span class="badge {} px-3 py-2" style="border-radius:50px;">{}</span>',
                           colors.get(obj.trang_thai), obj.get_trang_thai_display())
    trang_thai_badge.short_description = "Trạng thái"

    def duyet_hoan_tien(self, request, queryset):
        queryset.update(trang_thai='da_hoan_tien', ngay_xu_ly=timezone.now())
        self.message_user(request, "✅ Đã duyệt hoàn tiền!")
    duyet_hoan_tien.short_description = "✅ Duyệt hoàn tiền"

    def tu_choi_yeu_cau(self, request, queryset):
        queryset.update(trang_thai='da_tu_choi', ngay_xu_ly=timezone.now())
        self.message_user(request, "❌ Đã từ chối yêu cầu!")
    tu_choi_yeu_cau.short_description = "❌ Từ chối"


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('nguoi_dung', 'short_message', 'is_bot_badge', 'ngay_tao')
    list_filter = ('is_bot', 'ngay_tao')
    search_fields = ('nguoi_dung__username', 'message')
    ordering = ('-ngay_tao',)

    def short_message(self, obj):
        if not obj.message:
            return "(Tin nhắn trống)"
        if len(obj.message) > 80:
            return obj.message[:80] + "..."
        return obj.message
    short_message.short_description = "Nội dung"

    def is_bot_badge(self, obj):
        return format_html('<span class="badge {}">{}</span>',
                        'bg-success' if obj.is_bot else 'bg-primary', 
                        '🤖 Bot' if obj.is_bot else '👤 User')
    is_bot_badge.short_description = "Loại tin nhắn"


# ====================== ĐĂNG KÝ CÁC MODEL CÒN LẠI ======================
admin.site.register(NguoiDung)
admin.site.register(DanhMuc)
admin.site.register(GioHang)
admin.site.register(ChiTietDonHang)
admin.site.register(KhuyenMai)
admin.site.register(UserKhuyenMai)