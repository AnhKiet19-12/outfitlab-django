from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class NguoiDung(AbstractUser):
    ho_ten = models.CharField(max_length=100, blank=True, verbose_name="Họ tên")
    dia_chi = models.TextField(blank=True, verbose_name="Địa chỉ")
    so_dien_thoai = models.CharField(max_length=15, blank=True, verbose_name="Số điện thoại")
    chieu_cao = models.FloatField(null=True, blank=True, verbose_name="Chiều cao (cm)")
    can_nang = models.FloatField(null=True, blank=True, verbose_name="Cân nặng (kg)")
    so_thich = models.CharField(max_length=200, blank=True, verbose_name="Sở thích phối đồ")

    # Hạng thành viên
    hang_thanh_vien = models.CharField(
        max_length=20,
        choices=[
            ('dong', 'Đồng'),
            ('bac', 'Bạc'),
            ('vang', 'Vàng'),
            ('bachkim', 'Bạch Kim'),
            ('kimcuong', 'Kim Cương')
        ],
        default='dong',
        verbose_name="Hạng thành viên"
    )

    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/macdinh.png',
        blank=True,
        null=True,
        verbose_name="Ảnh đại diện"
    )

    email_verified = models.BooleanField(default=False, verbose_name="Email đã xác thực")
    otp = models.CharField(max_length=6, blank=True, null=True, verbose_name="Mã OTP")
    otp_expiry = models.DateTimeField(blank=True, null=True, verbose_name="Thời hạn OTP")

    class Meta:
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"

    def tinh_hang_thanh_vien(self):
        tong_tien = self.donhang_set.aggregate(models.Sum('tong_tien'))['tong_tien__sum'] or 0
        if tong_tien >= 50_000_000:
            return 'kimcuong'
        elif tong_tien >= 20_000_001:
            return 'bachkim'
        elif tong_tien >= 5_000_001:
            return 'vang'
        elif tong_tien >= 1_000_001:
            return 'bac'
        else:
            return 'dong'

    def cap_nhat_hang_thanh_vien(self):
        hang_moi = self.tinh_hang_thanh_vien()
        if self.hang_thanh_vien != hang_moi:
            self.hang_thanh_vien = hang_moi
            self.save(update_fields=['hang_thanh_vien'])
        return hang_moi

    def __str__(self):
        return self.ho_ten or self.username


class DanhMuc(models.Model):
    ten_danh_muc = models.CharField(max_length=100, verbose_name="Tên danh mục")
    
    # Phân biệt rõ ràng danh mục theo giới tính
    gioi_tinh_hop_le = models.CharField(
        max_length=20,
        choices=[
            ('nam', 'Nam'),
            ('nu', 'Nữ'),
            ('unisex', 'Unisex'),
        ],
        default='unisex',
        verbose_name="Giới tính áp dụng"
    )

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"
        ordering = ['ten_danh_muc', 'gioi_tinh_hop_le']
        
        # Quan trọng: Cho phép cùng tên danh mục nhưng khác giới tính
        unique_together = ('ten_danh_muc', 'gioi_tinh_hop_le')

    def __str__(self):
        return f"{self.ten_danh_muc} ({self.get_gioi_tinh_hop_le_display()})"

    @property
    def display_name(self):
        """Tên hiển thị đẹp hơn"""
        if self.gioi_tinh_hop_le == 'unisex':
            return f"{self.ten_danh_muc} (Unisex)"
        elif self.gioi_tinh_hop_le == 'nam':
            return f"{self.ten_danh_muc} Nam"
        else:
            return f"{self.ten_danh_muc} Nữ"

class SanPham(models.Model):
    ten_san_pham = models.CharField(max_length=200, verbose_name="Tên sản phẩm")
    mo_ta = models.TextField(verbose_name="Mô tả sản phẩm")
    hinh_anh = models.ImageField(upload_to='sanpham/', verbose_name="Hình ảnh chính")
    
    danh_muc = models.ForeignKey(DanhMuc, on_delete=models.CASCADE, 
                                related_name='san_pham', verbose_name="Danh mục")

    loai_san_pham = models.CharField(max_length=20, choices=[
        ('ao', 'Áo'),
        ('quan', 'Quần'),
        ('phu_kien', 'Phụ kiện')
    ], default='ao', verbose_name="Loại sản phẩm")

    gioi_tinh = models.CharField(max_length=20, choices=[
        ('nam', 'Nam'),
        ('nu', 'Nữ'),
        ('unisex', 'Unisex')
    ], default='unisex', verbose_name="Giới tính")

    phong_cach = models.CharField(max_length=100, blank=True, verbose_name="Phong cách")
    chat_lieu = models.CharField(max_length=100, blank=True, verbose_name="Chất liệu")
    xuat_xu = models.CharField(max_length=100, default="Việt Nam", verbose_name="Xuất xứ")
    tags_phoi_do = models.CharField(max_length=100, blank=True, verbose_name="Tags phối đồ")

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"

    def __str__(self):
        return self.ten_san_pham


class SanPhamBienThe(models.Model):
    san_pham = models.ForeignKey(SanPham, on_delete=models.CASCADE, 
                                related_name='bien_the', verbose_name="Sản phẩm")

    mau_sac = models.CharField(max_length=50, verbose_name="Màu sắc")
    kich_co = models.CharField(max_length=20, verbose_name="Kích cỡ")
    gia = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá")
    so_luong = models.IntegerField(default=10, verbose_name="Số lượng tồn")

    hinh_anh = models.ImageField(upload_to='sanpham/bienthe/', blank=True, null=True, 
                                verbose_name="Hình ảnh biến thể")

    class Meta:
        unique_together = ('san_pham', 'mau_sac', 'kich_co')
        verbose_name = "Biến thể sản phẩm"
        verbose_name_plural = "Biến thể sản phẩm"

    def __str__(self):
        return f"{self.san_pham.ten_san_pham} - {self.mau_sac} - {self.kich_co}"


class DanhGiaSanPham(models.Model):
    san_pham = models.ForeignKey(SanPham, on_delete=models.CASCADE, 
                                related_name='danh_gia', verbose_name="Sản phẩm")
    nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, verbose_name="Người đánh giá")
    so_sao = models.PositiveSmallIntegerField(choices=[(1,'1'),(2,'2'),(3,'3'),(4,'4'),(5,'5')], 
                                             verbose_name="Số sao")
    noi_dung = models.TextField(verbose_name="Nội dung đánh giá")
    hinh_anh = models.ImageField(upload_to='reviews/', blank=True, null=True, verbose_name="Hình ảnh đánh giá")
    ngay_danh_gia = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đánh giá")

    class Meta:
        ordering = ['-ngay_danh_gia']
        verbose_name = "Đánh giá sản phẩm"
        verbose_name_plural = "Đánh giá sản phẩm"

    def __str__(self):
        return f"{self.nguoi_dung} - {self.san_pham} ({self.so_sao} sao)"


class BangSize(models.Model):
    san_pham = models.ForeignKey(SanPham, on_delete=models.CASCADE, 
                                related_name='bang_size', verbose_name="Sản phẩm")
    kich_co = models.CharField(max_length=20, verbose_name="Kích cỡ")

    # Áo
    chieu_rong = models.CharField(max_length=50, blank=True, verbose_name="Chiều rộng ngực (cm)")
    chieu_dai_ao = models.CharField(max_length=50, blank=True, verbose_name="Chiều dài áo (cm)")
    chieu_dai_tay = models.CharField(max_length=50, blank=True, verbose_name="Chiều dài tay áo (cm)")

    # Quần
    chieu_cao_tu = models.CharField(max_length=20, blank=True, verbose_name="Chiều cao từ (cm)")
    chieu_cao_den = models.CharField(max_length=20, blank=True, verbose_name="Chiều cao đến (cm)")
    can_nang_tu = models.CharField(max_length=20, blank=True, verbose_name="Cân nặng từ (kg)")
    can_nang_den = models.CharField(max_length=20, blank=True, verbose_name="Cân nặng đến (kg)")
    chieu_dai_quan = models.CharField(max_length=50, blank=True, verbose_name="Chiều dài quần (cm)")
    vong_eo = models.CharField(max_length=50, blank=True, verbose_name="Vòng eo (cm)")

    mo_ta = models.CharField(max_length=200, blank=True, verbose_name="Ghi chú thêm")

    class Meta:
        unique_together = ('san_pham', 'kich_co')
        verbose_name = "Bảng size"
        verbose_name_plural = "Bảng size"

    def __str__(self):
        return f"{self.san_pham.ten_san_pham} - {self.kich_co}"


class GioHang(models.Model):
    nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, verbose_name="Người dùng")
    san_pham = models.ForeignKey(SanPham, on_delete=models.CASCADE, verbose_name="Sản phẩm")
    bien_the = models.ForeignKey(SanPhamBienThe, on_delete=models.CASCADE, 
                                null=True, blank=True, verbose_name="Biến thể")
    so_luong = models.IntegerField(default=1, verbose_name="Số lượng")

    class Meta:
        unique_together = ('nguoi_dung', 'bien_the')
        verbose_name = "Giỏ hàng"
        verbose_name_plural = "Giỏ hàng"

    def __str__(self):
        return f"{self.nguoi_dung} - {self.san_pham}"


class DonHang(models.Model):
    nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, verbose_name="Người dùng")
    ngay_dat = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đặt hàng")
    tong_tien = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Tổng tiền")

    TRANG_THAI_CHOICES = [
        ('cho_xac_nhan', 'Chờ xác nhận'),
        ('da_xac_nhan', 'Đã xác nhận'),
        ('dang_giao', 'Đang giao hàng'),
        ('da_giao', 'Đã giao hàng'),
        ('da_huy', 'Đã hủy'),
    ]
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICES, 
                                 default='cho_xac_nhan', verbose_name="Trạng thái")

    ma_giam_gia = models.CharField(max_length=50, blank=True, verbose_name="Mã giảm giá")
    dia_chi_giao = models.TextField(blank=True, null=True, verbose_name="Địa chỉ giao hàng")
    ho_ten_nhan = models.CharField(max_length=100, blank=True, verbose_name="Họ tên người nhận")
    so_dien_thoai_nhan = models.CharField(max_length=15, blank=True, verbose_name="SĐT người nhận")

    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"

    def __str__(self):
        return f"Đơn #{self.id} - {self.nguoi_dung}"


class ChiTietDonHang(models.Model):
    don_hang = models.ForeignKey(DonHang, on_delete=models.CASCADE, verbose_name="Đơn hàng")
    san_pham = models.ForeignKey(SanPham, on_delete=models.CASCADE, verbose_name="Sản phẩm")
    so_luong = models.IntegerField(verbose_name="Số lượng")
    gia = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giá")

    class Meta:
        verbose_name = "Chi tiết đơn hàng"
        verbose_name_plural = "Chi tiết đơn hàng"

    def __str__(self):
        return f"CT Đơn #{self.don_hang.id} - {self.san_pham}"


class KhuyenMai(models.Model):
    ma_khuyen_mai = models.CharField(max_length=50, unique=True, verbose_name="Mã khuyến mãi")
    ten_khuyen_mai = models.CharField(max_length=100, verbose_name="Tên khuyến mãi")
    
    loai_giam = models.CharField(max_length=20, choices=[
        ('phan_tram', 'Giảm phần trăm'),
        ('tien', 'Giảm số tiền'),
        ('freeship', 'Freeship'),
    ], verbose_name="Loại giảm giá")
    
    gia_tri = models.IntegerField(verbose_name="Giá trị giảm")
    ngay_bat_dau = models.DateField(verbose_name="Ngày bắt đầu")
    ngay_ket_thuc = models.DateField(verbose_name="Ngày kết thúc")

    doi_tuong = models.CharField(max_length=20, choices=[
        ('all', 'Tất cả'), ('dong', 'Đồng'), ('bac', 'Bạc'), 
        ('vang', 'Vàng'), ('bachkim', 'Bạch Kim'), ('kimcuong', 'Kim Cương')
    ], default='all', verbose_name="Đối tượng")

    is_vip = models.BooleanField(default=False, verbose_name="Voucher VIP")
    thoi_han_ngay = models.IntegerField(default=30, verbose_name="Thời hạn (ngày)")
    so_luong_con = models.IntegerField(default=9999, verbose_name="Số lượng còn lại")
    mo_ta = models.TextField(blank=True, verbose_name="Mô tả")

    class Meta:
        verbose_name = "Khuyến mãi / Voucher"
        verbose_name_plural = "Khuyến mãi / Voucher"

    def __str__(self):
        return f"{self.ten_khuyen_mai} ({self.ma_khuyen_mai})"


class UserKhuyenMai(models.Model):
    nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, 
                                  related_name='my_vouchers', verbose_name="Người dùng")
    khuyen_mai = models.ForeignKey(KhuyenMai, on_delete=models.CASCADE, verbose_name="Khuyến mãi")
    
    da_su_dung = models.BooleanField(default=False, verbose_name="Đã sử dụng")
    ngay_nhan = models.DateTimeField(auto_now_add=True, verbose_name="Ngày nhận")
    ngay_su_dung = models.DateTimeField(null=True, blank=True, verbose_name="Ngày sử dụng")

    class Meta:
        unique_together = ('nguoi_dung', 'khuyen_mai')
        verbose_name = "Voucher của người dùng"
        verbose_name_plural = "Voucher của người dùng"

    def __str__(self):
        return f"{self.nguoi_dung} - {self.khuyen_mai.ten_khuyen_mai}"


class YeuCauHoanTien(models.Model):
    TRANG_THAI_CHOICES = [
        ('cho_xu_ly', 'Chờ xử lý'),
        ('dang_xu_ly', 'Đang xử lý'),
        ('da_hoan_tien', 'Đã hoàn tiền'),
        ('da_tu_choi', 'Từ chối'),
    ]

    don_hang = models.ForeignKey(DonHang, on_delete=models.CASCADE, 
                                related_name='yeu_cau_hoan_tien', verbose_name="Đơn hàng")
    san_pham = models.ForeignKey(SanPham, on_delete=models.CASCADE, verbose_name="Sản phẩm")
    nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, verbose_name="Người dùng")

    ly_do = models.CharField(max_length=100, verbose_name="Lý do")
    mo_ta = models.TextField(blank=True, verbose_name="Mô tả chi tiết")
    hinh_anh = models.ImageField(upload_to='hoan_tien/', blank=True, null=True, verbose_name="Hình ảnh minh chứng")

    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICES, 
                                 default='cho_xu_ly', verbose_name="Trạng thái")
    ngay_yeu_cau = models.DateTimeField(auto_now_add=True, verbose_name="Ngày yêu cầu")
    ngay_xu_ly = models.DateTimeField(null=True, blank=True, verbose_name="Ngày xử lý")

    class Meta:
        ordering = ['-ngay_yeu_cau']
        verbose_name = "Yêu cầu hoàn tiền"
        verbose_name_plural = "Yêu cầu hoàn tiền"

    def __str__(self):
        return f"Yêu cầu #{self.id} - Đơn #{self.don_hang.id}"


class ChatMessage(models.Model):
    nguoi_dung = models.ForeignKey(NguoiDung, on_delete=models.CASCADE, 
                                  related_name='chat_history', verbose_name="Người dùng")
    message = models.TextField(
        verbose_name="Nội dung tin nhắn",
        help_text="Hỗ trợ emoji và tiếng Việt"
    )
    is_bot = models.BooleanField(default=False, verbose_name="Là tin nhắn Bot")
    ngay_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày gửi")

    class Meta:
        ordering = ['ngay_tao']
        verbose_name = "Tin nhắn Chat"
        verbose_name_plural = "Lịch sử Chat"
        db_table = 'chatmessage'

    def __str__(self):
        return f"{self.nguoi_dung.username} - {'Bot' if self.is_bot else 'User'}"