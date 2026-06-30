from django.urls import path
from . import views

urlpatterns = [
    # ==================== TRANG CHÍNH ====================
    path('', views.trang_chu, name='trang_chu'),

    # ==================== XÁC THỰC ====================
    path('dang-ky/', views.dang_ky, name='dang_ky'),
    path('dang-nhap/', views.dang_nhap, name='dang_nhap'),
    path('dang-xuat/', views.dang_xuat, name='dang_xuat'),

    # ==================== Quên mật khẩu ====================
    path('quen-mat-khau/', views.quen_mat_khau, name='quen_mat_khau'),
    path('xac-nhan-otp/', views.xac_nhan_otp, name='xac_nhan_otp'),
    path('dat-lai-mat-khau/', views.dat_lai_mat_khau, name='dat_lai_mat_khau'),

    # ==================== SẢN PHẨM ====================
    path('san-pham/', views.danh_sach_san_pham, name='danh_sach_san_pham'),
    path('san-pham/<int:pk>/', views.chi_tiet_san_pham, name='chi_tiet_san_pham'),
    path('san-pham/<int:pk>/danh-gia/', views.danh_gia_san_pham, name='danh_gia_san_pham'),

    # ==================== GIỎ HÀNG & THANH TOÁN ====================
    path('them-gio/<int:pk>/', views.them_vao_gio, name='them_vao_gio'),
    path('xoa-khoi-gio/<int:item_id>/', views.xoa_khoi_gio, name='xoa_khoi_gio'),
    path('mua-ngay/<int:pk>/', views.mua_ngay, name='mua_ngay'),
    path('gio-hang/', views.gio_hang, name='gio_hang'),
    path('thanh-toan/', views.thanh_toan, name='thanh_toan'),
    path('don-hang/', views.don_hang_cua_toi, name='don_hang'),
    path('don-hang/xac-nhan-nhan/<int:don_id>/', views.xac_nhan_nhan_hang, name='xac_nhan_nhan_hang'),

    # ==================== PHỐI ĐỒ & TƯ VẤN ====================
    path('phoi-do/', views.phoi_do, name='phoi_do'),
    path('phoi-do/ai/', views.phoi_do_ai, name='phoi_do_ai'),
    path('chatbot/', views.chatbot, name='chatbot'),

    # ==================== TÀI KHOẢN NGƯỜI DÙNG ====================
    path('profile/', views.cap_nhat_profile, name='profile'),
    path('lich-su/', views.lich_su_don_hang, name='lich_su_don_hang'),
    path('voucher-cua-toi/', views.voucher_cua_toi, name='voucher_cua_toi'),
    path('nhan-voucher-hang-ngay/', views.nhan_voucher_hang_ngay, name='nhan_voucher_hang_ngay'),

    # ==================== VOUCHER & SỰ KIỆN ====================
    path('su-kien-voucher/', views.su_kien_voucher, name='su_kien_voucher'),
    path('nhan-voucher/<str:ma_khuyen_mai>/', views.nhan_voucher_event, name='nhan_voucher_event'),
    path('tao-voucher-mau/', views.tao_voucher_mau, name='tao_voucher_mau'),

    # ==================== ADMIN ====================
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # ==================== THANH TOÁN ONLINE ====================
    path('thanh-toan/zalopay-return/', views.zalopay_return, name='zalopay_return'),
    path('thanh-toan/zalopay-callback/', views.zalopay_callback, name='zalopay_callback'),


    # ==================== HOÀN TIỀN / TRẢ HÀNG ====================
    path('hoan-tien/', views.lich_su_hoan_tien, name='lich_su_hoan_tien'),
    path('yeu-cau-hoan-tien/<int:don_id>/<int:sanpham_id>/', views.yeu_cau_hoan_tien, name='yeu_cau_hoan_tien'),


]    