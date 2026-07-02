from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg, F
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.http import HttpResponse, JsonResponse  
from django.template.loader import render_to_string
from django.db.models import Avg, Sum, Min, Max
import json
import qrcode
from io import BytesIO
import base64
import random
from datetime import timedelta
from datetime import datetime
import hashlib
import hmac
import requests
from .models import *
from .forms import ProfileForm, YeuCauHoanTienForm
from openai import OpenAI
from dotenv import load_dotenv
import os
from django.db.models import Q, Min
import re
import google.generativeai as genai
from django.db.models.functions import ExtractYear, ExtractMonth, TruncDate
from django.utils import timezone
from django.urls import reverse

ZALOPAY_CONFIG = {
    'appid': 554,
    'key1': '8NdU5pG5R2spGHGhyO99HN1OhD8IQJBn',
    'key2': 'uUfsWgfLkRLzq6W2uNXTCxrfxs51auny',
    'endpoint': 'https://sb-openapi.zalopay.vn/v2/create',
    'return_url': 'http://127.0.0.1:8000/thanh-toan/zalopay-return/',
}

# ====================== AUTH ======================
def dang_ky(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST.get('email')
        ho_ten = request.POST.get('ho_ten', '')
        so_dien_thoai = request.POST.get('so_dien_thoai', '')

        if NguoiDung.objects.filter(username=username).exists():
            messages.error(request, 'Tên tài khoản đã tồn tại!')
            return render(request, 'dang_ky.html')

        user = NguoiDung.objects.create_user(
            username=username, 
            email=email, 
            password=password,
            ho_ten=ho_ten, 
            so_dien_thoai=so_dien_thoai,
            avatar='avatars/macdinh.png'   
        )
        
        messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
        return redirect('dang_nhap')

    return render(request, 'dang_ky.html')


def dang_nhap(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            login(request, user)
            
            # Xử lý next URL (từ admin hoặc trang khác)
            next_url = request.GET.get('next')
            
            # Nếu là Staff/Admin → ưu tiên vào Admin
            if user.is_staff or user.is_superuser:
                messages.success(request, f'🎉 Đăng nhập Admin thành công - {user.username}')
                if next_url and next_url.startswith('/admin'):
                    return redirect(next_url)
                return redirect('/admin/')  # hoặc 'admin:index'
            
            # User thường
            messages.success(request, 'Đăng nhập thành công!')
            return redirect(next_url or 'trang_chu')
        
        else:
            messages.error(request, '❌ Sai tên tài khoản hoặc mật khẩu!')
    
    return render(request, 'dang_nhap.html')


def dang_xuat(request):
    logout(request)
    return redirect('trang_chu')


# ====================== QUÊN MẬT KHẨU ======================
def quen_mat_khau(request):
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        
        if not email:
            messages.error(request, 'Vui lòng nhập email!')
            return render(request, 'quen_mat_khau.html')

        try:
            user = NguoiDung.objects.get(email=email)
            
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            
            user.otp = otp
            user.otp_expiry = timezone.now() + timedelta(minutes=10)
            user.save()

            send_mail(
                subject='Mã OTP đặt lại mật khẩu - Thời Trang VN',
                message=f'Mã OTP của bạn là: {otp}\n\nMã này sẽ hết hạn sau 10 phút.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, f'✅ Mã OTP đã được gửi đến email: {email}')
            # Truyền email qua query string
            return redirect(f"{reverse('xac_nhan_otp')}?email={email}")

        except NguoiDung.DoesNotExist:
            messages.error(request, '❌ Email này không tồn tại trong hệ thống!')

    return render(request, 'quen_mat_khau.html')


def xac_nhan_otp(request):
    email = request.GET.get('email') or request.POST.get('email') or request.session.get('reset_email')

    if request.method == 'POST':
        otp = request.POST.get('otp')

        if not email:
            messages.error(request, 'Email không hợp lệ!')
            return render(request, 'xac_nhan_otp.html', {'email': email})

        try:
            user = NguoiDung.objects.get(email=email)
            if user.otp == otp and user.otp_expiry and user.otp_expiry > timezone.now():
                request.session['reset_email'] = email
                messages.success(request, 'Xác thực OTP thành công!')
                return redirect('dat_lai_mat_khau')
            else:
                messages.error(request, 'Mã OTP không đúng hoặc đã hết hạn!')
        except NguoiDung.DoesNotExist:
            messages.error(request, 'Email không tồn tại trong hệ thống!')

    return render(request, 'xac_nhan_otp.html', {'email': email})


def dat_lai_mat_khau(request):
    if request.method == 'POST':
        email = request.session.get('reset_email')
        password = request.POST.get('password')
        if email:
            user = NguoiDung.objects.get(email=email)
            user.set_password(password)
            user.otp = None
            user.otp_expiry = None
            user.save()
            messages.success(request, 'Đặt lại mật khẩu thành công! Vui lòng đăng nhập lại.')
            return redirect('dang_nhap')
    return render(request, 'dat_lai_mat_khau.html')


# ====================== PROFILE (Avatar + Xóa avatar) ======================
@login_required
def cap_nhat_profile(request):
    # Cập nhật hạng thành viên
    request.user.cap_nhat_hang_thanh_vien()

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        delete_avatar = request.POST.get('delete_avatar') == 'true'

        if form.is_valid():
            if delete_avatar:
                if request.user.avatar and request.user.avatar.name != 'avatars/macdinh.png':
                    try:
                        request.user.avatar.delete(save=False)
                    except:
                        pass
                request.user.avatar = None

            form.save()
            request.user.cap_nhat_hang_thanh_vien()
            messages.success(request, 'Cập nhật thông tin thành công!')
            return redirect('profile')

    else:
        form = ProfileForm(instance=request.user)

    # === XÓA CÁC MESSAGES CŨ TRƯỚC KHI HIỂN THỊ ===
    storage = messages.get_messages(request)
    storage.used = True   # Đánh dấu đã đọc để xóa

    # Thông tin hạng
    hang_info = {
        'dong': {'ten': 'Đồng', 'icon': 'Dong.png', 'mau': '#cd7f32', 'uu_dai': '0% giảm giá'},
        'bac': {'ten': 'Bạc', 'icon': 'Bac.png', 'mau': '#c0c0c0', 'uu_dai': '5% giảm giá'},
        'vang': {'ten': 'Vàng', 'icon': 'Vang.png', 'mau': '#ffd700', 'uu_dai': '10% giảm giá'},
        'bachkim': {'ten': 'Bạch Kim', 'icon': 'Bachkim.png', 'mau': '#e5e4e2', 'uu_dai': '15% giảm giá'},
        'kimcuong': {'ten': 'Kim Cương', 'icon': 'Kimcuong.png', 'mau': '#b9f2ff', 'uu_dai': '20% giảm giá + freeship'},
    }

    current_hang_key = request.user.hang_thanh_vien
    current_hang = hang_info.get(current_hang_key, hang_info['dong'])

    tong_chi_tieu = request.user.donhang_set.aggregate(Sum('tong_tien'))['tong_tien__sum'] or 0

    return render(request, 'thongtin.html', {
        'form': form,
        'hang_info': hang_info,
        'current_hang': current_hang,
        'current_hang_key': current_hang_key,
        'tong_chi_tieu': tong_chi_tieu,
    })

def dang_xuat(request):
    logout(request)
    return redirect('trang_chu')

# ====================== CUSTOMER ======================
def trang_chu(request):
    # Lấy sản phẩm nổi bật + prefetch dữ liệu liên quan
    san_pham_noi_bat = SanPham.objects.prefetch_related('bien_the', 'danh_gia').all()[:8]
    
    san_pham_list = []
    for sp in san_pham_noi_bat:
        # === Giá min - max ===
        bien_the = sp.bien_the.all()
        if bien_the.exists():
            sp.gia_min = min(bt.gia for bt in bien_the)
            sp.gia_max = max(bt.gia for bt in bien_the)
        else:
            sp.gia_min = 0
            sp.gia_max = 0

        # === Đánh giá ===
        danh_gia = sp.danh_gia.all()
        sp.tong_danh_gia = danh_gia.count()
        avg = danh_gia.aggregate(Avg('so_sao'))['so_sao__avg']
        sp.avg_rating = round(avg, 1) if avg else 0

        # === Lượt mua ===
        sp.luot_mua = ChiTietDonHang.objects.filter(san_pham=sp).aggregate(
            total=Sum('so_luong')
        )['total'] or 0

        san_pham_list.append(sp)

    # Gợi ý theo giới tính nếu người dùng đã đăng nhập
    goi_y_theo_gioi_tinh = None
    if request.user.is_authenticated:
        if hasattr(request.user, 'gioi_tinh') and request.user.gioi_tinh == 'Nam':
            goi_y_theo_gioi_tinh = SanPham.objects.filter(gioi_tinh__in=['nam', 'unisex'])[:6]
        elif hasattr(request.user, 'gioi_tinh') and request.user.gioi_tinh == 'Nữ':
            goi_y_theo_gioi_tinh = SanPham.objects.filter(gioi_tinh__in=['nu', 'unisex'])[:6]

    return render(request, 'trang_chu.html', {
        'san_pham_noi_bat': san_pham_list,
        'goi_y_theo_gioi_tinh': goi_y_theo_gioi_tinh
    })

def danh_sach_san_pham(request):
    san_pham_qs = SanPham.objects.prefetch_related('bien_the', 'danh_gia').all()
    danh_muc_list = DanhMuc.objects.all()

    q = request.GET.get('q', '').strip()
    danh_muc_slug = request.GET.get('danh_muc')
    gioi_tinh = request.GET.get('gioi_tinh')      
    loai_san_pham = request.GET.get('loai_san_pham')
    gia_min = request.GET.get('gia_min')
    gia_max = request.GET.get('gia_max')
    sort = request.GET.get('sort')

    # ====================== LỌC GIỚI TÍNH TỪ URL ======================
    if gioi_tinh and gioi_tinh != 'all':
        if gioi_tinh == 'nam':
            san_pham_qs = san_pham_qs.filter(gioi_tinh='nam')
        elif gioi_tinh == 'nu':
            san_pham_qs = san_pham_qs.filter(gioi_tinh='nu')
        elif gioi_tinh == 'unisex':
            san_pham_qs = san_pham_qs.filter(gioi_tinh='unisex')
        else:
            gt_list = [x.strip() for x in gioi_tinh.split(',') if x.strip()]
            san_pham_qs = san_pham_qs.filter(gioi_tinh__in=gt_list)

    # ====================== TÌM KIẾM THÔNG MINH ======================
    if q:
        q_lower = q.lower()
        keywords = q_lower.split()

        # Xử lý giới tính trong từ khóa tìm kiếm (an toàn, không dùng replace)
        gioi_tinh_search = None
        if 'nam' in keywords:
            gioi_tinh_search = 'nam'
            keywords.remove('nam')
        elif 'nữ' in keywords:
            gioi_tinh_search = 'nu'
            keywords.remove('nữ')
        elif 'nu' in keywords:
            gioi_tinh_search = 'nu'
            keywords.remove('nu')

        if gioi_tinh_search:
            san_pham_qs = san_pham_qs.filter(gioi_tinh=gioi_tinh_search)

        # Ghép lại chuỗi tìm kiếm sau khi loại bỏ từ giới tính
        q_clean = ' '.join(keywords).strip()

        if q_clean:
            q_objects = Q(
                ten_san_pham__icontains=q_clean
            ) | Q(
                danh_muc__ten_danh_muc__icontains=q_clean
            )

            # Tìm kiếm từng từ khóa
            for keyword in keywords:
                if not keyword:
                    continue
                    
                q_objects |= Q(ten_san_pham__icontains=keyword)
                q_objects |= Q(mo_ta__icontains=keyword)
                q_objects |= Q(danh_muc__ten_danh_muc__icontains=keyword)
                q_objects |= Q(loai_san_pham__icontains=keyword)
                q_objects |= Q(tags_phoi_do__icontains=keyword)
                q_objects |= Q(bien_the__mau_sac__icontains=keyword)

                # Từ đồng nghĩa
                if keyword in ['ao', 'áo', 'thun', 'phong', 'somi', 'sơ mi']:
                    q_objects |= Q(loai_san_pham='ao')
                if keyword in ['quan', 'quần', 'jean', 'jeans', 'short', 'tay']:
                    q_objects |= Q(loai_san_pham='quan')
                if keyword in ['vay', 'váy', 'chân váy', 'midi', 'maxi', 'đầm']:
                    q_objects |= Q(ten_san_pham__icontains='váy') | Q(loai_san_pham='quan')

            san_pham_qs = san_pham_qs.filter(q_objects).distinct()

    # ====================== CÁC BỘ LỌC KHÁC ======================
    if danh_muc_slug:
        san_pham_qs = san_pham_qs.filter(
            danh_muc__ten_danh_muc__iexact=danh_muc_slug.replace('-', ' ')
        )

    if loai_san_pham:
        san_pham_qs = san_pham_qs.filter(loai_san_pham=loai_san_pham)

    # Lọc giá
    if gia_min or gia_max:
        bien_the_qs = SanPhamBienThe.objects.filter(san_pham__in=san_pham_qs)
        if gia_min:
            bien_the_qs = bien_the_qs.filter(gia__gte=gia_min)
        if gia_max:
            bien_the_qs = bien_the_qs.filter(gia__lte=gia_max)
        valid_ids = bien_the_qs.values_list('san_pham_id', flat=True).distinct()
        san_pham_qs = san_pham_qs.filter(id__in=valid_ids)

    # ====================== SẮP XẾP ======================
    if sort == 'moi_nhat':
        san_pham_qs = san_pham_qs.order_by('-id')
    elif sort in ['ban_chay', 'pho_bien'] or not sort:
        san_pham_qs = san_pham_qs.annotate(
            so_luong_ban=Count('chitietdonhang')
        ).order_by('-so_luong_ban')
    elif sort == 'gia_thap':
        san_pham_qs = san_pham_qs.annotate(
            gia_min=Min('bien_the__gia')
        ).order_by('gia_min')
    elif sort == 'gia_cao':
        san_pham_qs = san_pham_qs.annotate(
            gia_min=Min('bien_the__gia')
        ).order_by('-gia_min')
    else:
        san_pham_qs = san_pham_qs.annotate(
            so_luong_ban=Count('chitietdonhang')
        ).order_by('-so_luong_ban')

    # ====================== CHUẨN BỊ DỮ LIỆU ======================
    san_pham = []
    for sp in san_pham_qs:
        bien_the = list(sp.bien_the.all())
        if bien_the:
            prices = [bt.gia for bt in bien_the]
            sp.gia_min = min(prices)
            sp.gia_max = max(prices)
        else:
            sp.gia_min = sp.gia_max = 0

        danh_gia = sp.danh_gia.all()
        sp.tong_danh_gia = danh_gia.count()
        avg = danh_gia.aggregate(Avg('so_sao'))['so_sao__avg']
        sp.avg_rating = round(avg, 1) if avg else 0

        sp.luot_mua = ChiTietDonHang.objects.filter(san_pham=sp).aggregate(
            total=Sum('so_luong'))['total'] or 0

        san_pham.append(sp)

    # AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('product_grid.html', {'san_pham': san_pham})
        return JsonResponse({'html': html})

    return render(request, 'danh_sach_san_pham.html', {
        'san_pham': san_pham,
        'danh_muc': danh_muc_list,
        'q': q,  # giữ nguyên q gốc để hiển thị trong ô tìm kiếm
        'selected_danh_muc': danh_muc_slug,
        'selected_gender': gioi_tinh,
    })

def chi_tiet_san_pham(request, pk):
    sp = get_object_or_404(SanPham, pk=pk)
    
    # Lấy biến thể + chuyển đường dẫn ảnh thành .url đầy đủ
    bien_the = []
    for bt in sp.bien_the.all():
        bien_the.append({
            'id': bt.id,
            'mau_sac': bt.mau_sac,
            'kich_co': bt.kich_co,
            'gia': float(bt.gia),
            'so_luong': bt.so_luong,
            'hinh_anh': bt.hinh_anh.url if bt.hinh_anh else None,   # ← Sửa ở đây
        })
    
    danh_gia = sp.danh_gia.all()[:8]
    tong_danh_gia = danh_gia.count()
    
    # Sửa lỗi import models
    from django.db.models import Avg
    avg_rating = sp.danh_gia.aggregate(Avg('so_sao'))['so_sao__avg']
    avg_rating = round(avg_rating, 1) if avg_rating else 0

    bang_size = sp.bang_size.all()

    return render(request, 'chi_tiet_san_pham.html', {
        'san_pham': sp,
        'bien_the_json': bien_the,          # ← Đã sửa
        'danh_gia': danh_gia,
        'tong_danh_gia': tong_danh_gia,
        'avg_rating': avg_rating,
        'bang_size': bang_size,
    })

# ====================== ĐÁNH GIÁ SẢN PHẨM ======================
@login_required
def danh_gia_san_pham(request, pk):
    sp = get_object_or_404(SanPham, pk=pk)

    if request.method == 'POST':
        so_sao = request.POST.get('so_sao')
        noi_dung = request.POST.get('noi_dung')
        hinh_anh = request.FILES.get('hinh_anh')

        if so_sao and noi_dung:
            DanhGiaSanPham.objects.create(
                san_pham=sp,
                nguoi_dung=request.user,
                so_sao=int(so_sao),
                noi_dung=noi_dung,
                hinh_anh=hinh_anh
            )
            messages.success(request, '✅ Cảm ơn bạn đã đánh giá sản phẩm!')
            return redirect('chi_tiet_san_pham', pk=pk)
        else:
            messages.error(request, 'Vui lòng chọn số sao và nhập nội dung đánh giá!')

    # Nếu GET hoặc lỗi thì redirect về trang chi tiết
    return redirect('chi_tiet_san_pham', pk=pk)

@login_required
def them_vao_gio(request, pk):
    bien_the = get_object_or_404(SanPhamBienThe, pk=pk)
    
    if bien_the.so_luong <= 0:
        messages.error(request, 'Sản phẩm đã hết hàng!')
        return redirect('chi_tiet_san_pham', pk=bien_the.san_pham.pk)

    # Sửa lại get_or_create đúng với bien_the
    gio, created = GioHang.objects.get_or_create(
        nguoi_dung=request.user, 
        bien_the=bien_the,
        defaults={'san_pham': bien_the.san_pham}
    )
    
    if not created:
        gio.so_luong += 1
        gio.save()

    messages.success(request, f'✅ Đã thêm {bien_the.san_pham.ten_san_pham} ({bien_the.mau_sac} - {bien_the.kich_co}) vào giỏ hàng!')
    return redirect('gio_hang')

@login_required
def xoa_khoi_gio(request, item_id):
    try:
        item = GioHang.objects.get(id=item_id, nguoi_dung=request.user)
        item.delete()
        return JsonResponse({'success': True})
    except GioHang.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Không tìm thấy sản phẩm'}, status=404)

@login_required
def gio_hang(request):
    gio = GioHang.objects.filter(nguoi_dung=request.user).select_related('bien_the', 'san_pham')
    
    for item in gio:
        item.thanh_tien = (item.bien_the.gia if item.bien_the else item.san_pham.gia or 0) * item.so_luong
    
    tong_tien = sum(item.thanh_tien for item in gio)
    
    # Lấy voucher chưa dùng
    vouchers = UserKhuyenMai.objects.filter(
        nguoi_dung=request.user,
        da_su_dung=False
    ).select_related('khuyen_mai').order_by('-ngay_nhan')

    return render(request, 'gio_hang.html', {
        'gio_hang': gio, 
        'tong_tien': tong_tien,
        'vouchers': vouchers,
        'phi_ship': 30000
    })

@login_required
def mua_ngay(request, pk):
    bien_the = get_object_or_404(SanPhamBienThe, pk=pk)
    
    if bien_the.so_luong <= 0:
        messages.error(request, 'Sản phẩm đã hết hàng!')
        return redirect('chi_tiet_san_pham', pk=bien_the.san_pham.pk)

    # Xóa giỏ hàng cũ để chỉ thanh toán sản phẩm này
    GioHang.objects.filter(nguoi_dung=request.user).delete()

    # Thêm sản phẩm vào giỏ hàng tạm
    GioHang.objects.create(
        nguoi_dung=request.user,
        san_pham=bien_the.san_pham,
        bien_the=bien_the,
        so_luong=1
    )

    return redirect('thanh_toan')

# ====================== PHỐI ĐỒ ======================
@login_required
def phoi_do(request):
    if request.method == 'POST':
        chieu_cao = float(request.POST.get('chieu_cao', 165))
        can_nang = float(request.POST.get('can_nang', 60))
        so_thich = request.POST.get('so_thich', '')
        muc_gia = int(request.POST.get('muc_gia', 500000))

        # Gợi ý theo sở thích + mức giá
        goi_y = SanPham.objects.filter(gia__lte=muc_gia)
        if so_thich:
            goi_y = goi_y.filter(phong_cach__in=so_thich.split(','))

        # Nếu người dùng đã chọn 1 sản phẩm
        san_pham_da_chon_id = request.POST.get('san_pham_da_chon')
        if san_pham_da_chon_id:
            sp_chon = get_object_or_404(SanPham, pk=san_pham_da_chon_id)
            # Gợi ý phụ kiện phù hợp
            goi_y = goi_y.exclude(pk=sp_chon.pk)[:6]

        return render(request, 'phoi_do_goi_y.html', {'goi_y': goi_y})

    # Form phối đồ
    return render(request, 'phoi_do.html')

@login_required
def them_phoi_vao_gio(request, pk):
    # Thêm sản phẩm từ gợi ý phối đồ vào giỏ
    return them_vao_gio(request, pk)

# ====================== CHATBOT ======================
@login_required
def chatbot(request):
    if request.method == 'POST':
        message = request.POST.get('message', '').lower()
        # Rule-based AI đơn giản (có thể thay bằng Grok API sau)
        if 'gợi ý' in message or 'phối đồ' in message:
            response = "Tôi gợi ý bạn thử áo sơ mi trắng phối quần jeans và giày sneaker! Bạn muốn xem sản phẩm nào?"
        elif 'giá' in message:
            response = "Sản phẩm đang có giá từ 199.000đ - 1.999.000đ. Bạn muốn xem theo mức giá nào?"
        elif 'khuyến mãi' in message:
            response = "Tháng này giảm 20% cho thành viên Vàng & Kim Cương!"
        else:
            response = "Cảm ơn bạn! Tôi có thể hỗ trợ tư vấn phối đồ, giá cả, đơn hàng. Bạn cần gì ạ?"
        return render(request, 'chatbot.html', {'response': response, 'message': message})
    return render(request, 'chatbot.html')


# ====================== THANH TOÁN ======================
@login_required
def thanh_toan(request):
    # LẤY SẢN PHẨM ĐÃ CHỌN
    selected_ids = request.GET.getlist('selected_items')

    if selected_ids:
        gio = GioHang.objects.filter(
            nguoi_dung=request.user, 
            id__in=selected_ids
        ).select_related('bien_the', 'san_pham')
    else:
        gio = GioHang.objects.filter(nguoi_dung=request.user).select_related('bien_the', 'san_pham')

    if not gio.exists():
        messages.warning(request, "Giỏ hàng trống!")
        return redirect('gio_hang')

    tong_tien_sp = sum(
        (item.bien_the.gia if item.bien_the else 0) * item.so_luong 
        for item in gio
    )

    vouchers = UserKhuyenMai.objects.filter(
        nguoi_dung=request.user,
        da_su_dung=False
    ).select_related('khuyen_mai').order_by('-ngay_nhan')

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'bank')
        ma_giam_gia = request.POST.get('ma_giam_gia', '').strip()
        ma_freeship = request.POST.get('ma_freeship', '').strip()

        ho_ten_nhan = request.POST.get('ho_ten_nhan', request.user.ho_ten)
        so_dien_thoai_nhan = request.POST.get('so_dien_thoai_nhan', request.user.so_dien_thoai)
        dia_chi_giao = request.POST.get('dia_chi_giao', request.user.dia_chi)

        # Xử lý voucher
        giam_gia = 0
        freeship = False
        user_voucher_giam = None
        user_voucher_fs = None

        for uv in vouchers:
            km = uv.khuyen_mai
            if km.ma_khuyen_mai == ma_giam_gia and not uv.da_su_dung:
                user_voucher_giam = uv
                if km.loai_giam == 'phan_tram':
                    giam_gia = int(tong_tien_sp * km.gia_tri / 100)
                elif km.loai_giam == 'tien':
                    giam_gia = km.gia_tri

            elif km.ma_khuyen_mai == ma_freeship and not uv.da_su_dung and km.loai_giam == 'freeship':
                user_voucher_fs = uv
                freeship = True

        phi_ship = 0 if freeship else 30000
        tong_thanh_toan = tong_tien_sp - giam_gia + phi_ship

        # Tạo đơn hàng
        don = DonHang.objects.create(
            nguoi_dung=request.user,
            tong_tien=tong_thanh_toan,
            ma_giam_gia=f"{ma_giam_gia}|{ma_freeship}".strip('|'),
            ho_ten_nhan=ho_ten_nhan,
            so_dien_thoai_nhan=so_dien_thoai_nhan,
            dia_chi_giao=dia_chi_giao,
            trang_thai='cho_xac_nhan'
        )

        # Tạo chi tiết đơn
        for item in gio:
            gia = item.bien_the.gia if item.bien_the else 0
            ChiTietDonHang.objects.create(
                don_hang=don,
                san_pham=item.san_pham,
                so_luong=item.so_luong,
                gia=gia
            )

        gio.delete()

        if user_voucher_giam:
            user_voucher_giam.da_su_dung = True
            user_voucher_giam.ngay_su_dung = timezone.now()
            user_voucher_giam.save()
        if user_voucher_fs:
            user_voucher_fs.da_su_dung = True
            user_voucher_fs.ngay_su_dung = timezone.now()
            user_voucher_fs.save()

        # ==================== THANH TOÁN ====================
        if payment_method == 'bank':   # ZaloPay
            try:
                appid = ZALOPAY_CONFIG['appid']
                key1 = ZALOPAY_CONFIG['key1']
                endpoint = ZALOPAY_CONFIG['endpoint']

                current_time = datetime.now()
                yymmdd = current_time.strftime("%y%m%d")
                trans_id = int(current_time.timestamp() * 1000)
                app_trans_id = f"{yymmdd}_{don.id}{trans_id}"[-40:]

                amount = int(tong_thanh_toan)

                embed_data = json.dumps({
                    "redirecturl": ZALOPAY_CONFIG['return_url'],
                    "don_id": str(don.id)
                }, separators=(',', ':'))

                items_list = [{
                    "itemid": f"SP{don.id}",
                    "itemname": f"Đơn hàng #{don.id}",
                    "itemprice": amount,
                    "quantity": 1
                }]
                items = json.dumps(items_list, separators=(',', ':'))

                apptime = int(current_time.timestamp() * 1000)

                raw_data = f"{appid}|{app_trans_id}|{request.user.username}|{amount}|{apptime}|{embed_data}|{items}"
                mac = hmac.new(key1.encode('utf-8'), raw_data.encode('utf-8'), hashlib.sha256).hexdigest()

                payload = {
                    "app_id": appid,
                    "app_trans_id": app_trans_id,
                    "app_user": request.user.username,
                    "app_time": apptime,
                    "amount": amount,
                    "item": items,
                    "embed_data": embed_data,
                    "description": f"Thanh toán đơn hàng #{don.id} - OutfitLab",
                    "mac": mac
                }

                response = requests.post(endpoint, json=payload, timeout=20)
                result = response.json()

                if result.get('return_code') == 1:
                    request.session['last_don_id'] = don.id   # Thêm dòng này
                    return JsonResponse({
                        'method': 'bank',
                        'order_url': result.get('order_url')
                    })
                else:
                    error_msg = result.get('sub_return_message') or result.get('return_message') or 'ZaloPay từ chối'
                    return JsonResponse({'error': error_msg}, status=400)

            except Exception as e:
                print("ZaloPay Exception:", str(e))
                return JsonResponse({'error': f'Lỗi ZaloPay: {str(e)}'}, status=500)

        elif payment_method == 'cod':
            return JsonResponse({
                'method': 'cod',
                'don_id': don.id
            })

        return JsonResponse({'error': 'Phương thức thanh toán không hợp lệ'}, status=400)

    # GET
    return render(request, 'thanh_toan.html', {
        'gio_hang': gio,
        'tong_tien': tong_tien_sp,
        'vouchers': vouchers,
        'phi_ship': 30000,
    })

@login_required
def zalopay_return(request):
    """Xử lý sau khi thanh toán ZaloPay (Return URL)"""
    apptransid = request.GET.get('apptransid')
    status = request.GET.get('status')

    if status == '1' and apptransid:  # Thanh toán thành công
        try:
            # Tách ID đơn hàng từ apptransid (ví dụ: 260630_1041782808722330)
            if '_' in apptransid:
                don_id_str = apptransid.split('_')[1]   # Lấy phần sau dấu _
                if don_id_str.isdigit():
                    don = DonHang.objects.get(id=don_id_str, nguoi_dung=request.user)
                    don.trang_thai = 'da_thanh_toan'
                    don.save()

                    # Xóa giỏ hàng
                    GioHang.objects.filter(nguoi_dung=request.user).delete()

                    messages.success(request, f'✅ Thanh toán đơn hàng #{don.id} thành công qua ZaloPay!')
                    return redirect('don_hang')   # Hoặc 'lich_su_don_hang'

        except DonHang.DoesNotExist:
            messages.warning(request, 'Không tìm thấy đơn hàng tương ứng.')
        except Exception as e:
            print("Zalopay return error:", e)

    # Trường hợp thất bại hoặc không có thông tin
    messages.warning(request, 'Thanh toán chưa hoàn tất hoặc bị hủy.')
    return redirect('lich_su_don_hang')

def zalopay_callback(request):
    """Callback từ ZaloPay (IPN)"""
    # Có thể để trống hoặc xử lý sau
    return HttpResponse("OK")

# ====================== LỊCH SỬ & PROFILE ======================
# ====================== ĐƠN HÀNG CỦA TÔI (Đang xử lý) ======================
@login_required
def don_hang_cua_toi(request):
    don_chua_giao = DonHang.objects.filter(
        nguoi_dung=request.user,
        trang_thai__in=['cho_xac_nhan', 'da_xac_nhan', 'dang_giao']
    ).prefetch_related('chitietdonhang_set__san_pham').order_by('-ngay_dat')
    
    return render(request, 'don_hang.html', {
        'don_chua_giao': don_chua_giao
    })


# ====================== XÁC NHẬN ĐÃ NHẬN HÀNG ======================
@login_required
def xac_nhan_nhan_hang(request, don_id):
    if request.method == 'POST':
        don = get_object_or_404(DonHang, id=don_id, nguoi_dung=request.user)
        
        # Chỉ cho phép xác nhận khi đơn đang ở trạng thái 'dang_giao'
        if don.trang_thai == 'dang_giao':
            don.trang_thai = 'da_giao'
            don.save()
            return JsonResponse({'success': True, 'message': 'Đã xác nhận nhận hàng thành công!'})
        else:
            return JsonResponse({'success': False, 'message': 'Không thể xác nhận đơn hàng này.'}, status=400)
    
    return JsonResponse({'success': False}, status=400)


# ====================== LỊCH SỬ ĐƠN HÀNG (Đã hoàn thành) ======================
@login_required
def lich_su_don_hang(request):
    don = DonHang.objects.filter(
        nguoi_dung=request.user,
        trang_thai__in=['da_giao', 'da_huy']
    ).prefetch_related('chitietdonhang_set__san_pham').order_by('-ngay_dat')
    
    return render(request, 'lich_su_don_hang.html', {'don_hang': don})
# ====================== ADMIN DASHBOARD ======================
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('trang_chu')
    tong_doanh_thu = DonHang.objects.aggregate(Sum('tong_tien'))['tong_tien__sum'] or 0
    so_don = DonHang.objects.count()
    san_ban_chay = SanPham.objects.annotate(so_luong_ban=Count('chitietdonhang')).order_by('-so_luong_ban')[:5]
    return render(request, 'admin_dashboard.html', {
        'tong_doanh_thu': tong_doanh_thu,
        'so_don': so_don,
        'san_ban_chay': san_ban_chay
    })

    # ====================== voucher ======================
@login_required
def voucher_cua_toi(request):
    vouchers = UserKhuyenMai.objects.filter(
        nguoi_dung=request.user,
        da_su_dung=False
    ).select_related('khuyen_mai').order_by('-ngay_nhan')

    return render(request, 'voucher_cua_toi.html', {'vouchers': vouchers})

@login_required
def nhan_voucher_hang_ngay(request):
    today = timezone.now().date()
    
    if UserKhuyenMai.objects.filter(nguoi_dung=request.user, ngay_nhan__date=today).exists():
        messages.info(request, "Bạn đã nhận voucher hôm nay rồi!")
        return redirect('voucher_cua_toi')

    # Tạo voucher freeship hoặc giảm giá
    km = KhuyenMai.objects.filter(ma_khuyen_mai='DAILYFREESHIP').first()
    if not km:
        km = KhuyenMai.objects.create(
            ma_khuyen_mai='DAILYFREESHIP',
            ten_khuyen_mai='Freeship 30K Hàng Ngày',
            loai_giam='freeship',
            gia_tri=30000,
            ngay_bat_dau=today,
            ngay_ket_thuc=today + timedelta(days=7),
        )
    
    UserKhuyenMai.objects.create(nguoi_dung=request.user, khuyen_mai=km)
    messages.success(request, "🎉 Bạn đã nhận voucher Freeship 30K thành công!")
    return redirect('voucher_cua_toi')

# ====================== VOUCHER ======================
@login_required
def voucher_cua_toi(request):
    vouchers = UserKhuyenMai.objects.filter(
        nguoi_dung=request.user,
        da_su_dung=False
    ).select_related('khuyen_mai').order_by('-ngay_nhan')

    return render(request, 'voucher_cua_toi.html', {
        'vouchers': vouchers,
        'user_hang': request.user.hang_thanh_vien
    })


@login_required
def su_kien_voucher(request):
    today = timezone.now().date()
    user_hang = request.user.hang_thanh_vien
    
    hang_level = {'dong': 0, 'bac': 1, 'vang': 2, 'bachkim': 3, 'kimcuong': 4}
    user_level = hang_level.get(user_hang, 0)

    # Voucher Thường (Ai cũng nhận được)
    vouchers_thuong = KhuyenMai.objects.filter(
        is_vip=False,
        ngay_bat_dau__lte=today,
        ngay_ket_thuc__gte=today,
        so_luong_con__gt=0
    ).order_by('ma_khuyen_mai')

    # Voucher Hạng Thành Viên (VIP)
    vouchers_vip = []
    for km in KhuyenMai.objects.filter(
        is_vip=True, 
        ngay_bat_dau__lte=today, 
        ngay_ket_thuc__gte=today
    ):
        required_level = hang_level.get(km.doi_tuong, 0)
        co_the_nhan = (km.doi_tuong == 'all') or (user_level >= required_level)
        
        vouchers_vip.append({
            'km': km,
            'co_the_nhan': co_the_nhan
        })

    return render(request, 'su_kien_voucher.html', {
        'vouchers_thuong': vouchers_thuong,
        'vouchers_vip': vouchers_vip,
        'user_hang': user_hang,
    })


@login_required
def nhan_voucher_event(request, ma_khuyen_mai):
    try:
        km = KhuyenMai.objects.get(ma_khuyen_mai=ma_khuyen_mai)
        today = timezone.now().date()

        if km.ngay_bat_dau > today or km.ngay_ket_thuc < today:
            messages.error(request, "Sự kiện voucher đã hết hạn!")
            return redirect('su_kien_voucher')

        # Kiểm tra hạng mức cho voucher VIP
        hang_level = {'dong':0, 'bac':1, 'vang':2, 'bachkim':3, 'kimcuong':4}
        user_level = hang_level.get(request.user.hang_thanh_vien, 0)
        required_level = hang_level.get(km.doi_tuong, 0)

        if user_level < required_level:
            messages.error(request, f"❌ Hạng thành viên của bạn ({request.user.hang_thanh_vien.capitalize()}) không đủ. Cần ít nhất {km.get_doi_tuong_display()}.")
            return redirect('su_kien_voucher')

        # Kiểm tra đã nhận chưa
        if UserKhuyenMai.objects.filter(nguoi_dung=request.user, khuyen_mai=km).exists():
            messages.info(request, "Bạn đã nhận voucher này rồi!")
            return redirect('voucher_cua_toi')

        # Tạo voucher
        UserKhuyenMai.objects.create(nguoi_dung=request.user, khuyen_mai=km)
        
        # Giảm số lượng nếu là voucher thường
        if not km.is_vip and km.so_luong_con < 9999:
            km.so_luong_con -= 1
            km.save()

        messages.success(request, f"🎉 Nhận thành công: {km.ten_khuyen_mai}!")
        return redirect('voucher_cua_toi')

    except KhuyenMai.DoesNotExist:
        messages.error(request, "Không tìm thấy voucher!")
        return redirect('su_kien_voucher')


@login_required
def voucher_count_api(request):
    count = UserKhuyenMai.objects.filter(nguoi_dung=request.user, da_su_dung=False).count()
    return JsonResponse({'count': count})

@login_required
def tao_voucher_mau(request):
    if not request.user.is_staff:
        return redirect('trang_chu')
        
    today = timezone.now().date()
    next_month = today + timedelta(days=30)
    
    # === VOUCHER THƯỜNG ===
    KhuyenMai.objects.get_or_create(
        ma_khuyen_mai='THUONG_5P',
        defaults={
            'ten_khuyen_mai': 'Giảm 5% Đơn Hàng',
            'loai_giam': 'phan_tram',
            'gia_tri': 5,
            'ngay_bat_dau': today,
            'ngay_ket_thuc': next_month,
            'is_vip': False,
            'thoi_han_ngay': 30,
            'doi_tuong': 'all'
        }
    )
    
    KhuyenMai.objects.get_or_create(
        ma_khuyen_mai='FREESHIP30',
        defaults={
            'ten_khuyen_mai': 'Freeship 30k',
            'loai_giam': 'freeship',
            'gia_tri': 30000,
            'ngay_bat_dau': today,
            'ngay_ket_thuc': next_month,
            'is_vip': False,
            'thoi_han_ngay': 7,
            'doi_tuong': 'all'
        }
    )
    
    # === VOUCHER VIP THEO HẠNG ===
    vip_data = [
        ('VIP_DONG5', 'Giảm 5% Hạng Đồng', 'phan_tram', 5, 'dong'),
        ('VIP_BAC8', 'Giảm 8% Hạng Bạc', 'phan_tram', 8, 'bac'),
        ('VIP_VANG12', 'Giảm 12% Hạng Vàng', 'phan_tram', 12, 'vang'),
        ('VIP_BK15', 'Giảm 15% Hạng Bạch Kim', 'phan_tram', 15, 'bachkim'),
        ('VIP_KC20', 'Giảm 20% + Freeship Hạng Kim Cương', 'phan_tram', 20, 'kimcuong'),
    ]
    
    for ma, ten, loai, gia_tri, doi_tuong in vip_data:
        KhuyenMai.objects.get_or_create(
            ma_khuyen_mai=ma,
            defaults={
                'ten_khuyen_mai': ten,
                'loai_giam': loai,
                'gia_tri': gia_tri,
                'ngay_bat_dau': today,
                'ngay_ket_thuc': today + timedelta(days=365*2),  # 2 năm
                'is_vip': True,
                'thoi_han_ngay': 9999,
                'doi_tuong': doi_tuong
            }
        )
    
    messages.success(request, "Đã tạo voucher mẫu thành công!")
    return redirect('su_kien_voucher')


# ====================== HOÀN TIỀN ======================
@login_required
def yeu_cau_hoan_tien(request, don_id, sanpham_id):
    don = get_object_or_404(DonHang, id=don_id, nguoi_dung=request.user)
    san_pham = get_object_or_404(SanPham, id=sanpham_id)

    if request.method == 'POST':
        form = YeuCauHoanTienForm(request.POST, request.FILES)
        
        if form.is_valid():
            yeu_cau = form.save(commit=False)
            yeu_cau.don_hang = don
            yeu_cau.san_pham = san_pham
            yeu_cau.nguoi_dung = request.user
            yeu_cau.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})

            messages.success(request, '✅ Yêu cầu đã được gửi thành công!')
            return redirect('lich_su_hoan_tien')
        
        else:
            # === DEBUG LỖI FORM ===
            print("Form errors:", form.errors)   # In ra console server
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': str(form.errors)
                }, status=400)

    form = YeuCauHoanTienForm()

    return render(request, 'yeu_cau_hoan_tien.html', {
        'form': form,
        'don': don,
        'san_pham': san_pham
    })

@login_required
def lich_su_hoan_tien(request):
    yeu_cau = YeuCauHoanTien.objects.filter(nguoi_dung=request.user).order_by('-ngay_yeu_cau')
    return render(request, 'lich_su_hoan_tien.html', {'yeu_cau_list': yeu_cau})

# ====================== CHAT AI - GOOGLE GEMINI ======================
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    generation_config={
        "temperature": 0.8,
        "max_output_tokens": 4096,
    }
)

# ====================== CHATBOT - TRỢ LÝ THỜI TRANG ======================
@login_required
def chatbot(request):
    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        
        if not message:
            return JsonResponse({'response': 'Chào bạn! 👋 Mình là Trợ lý thời trang. Hôm nay mình giúp bạn gì nào? 💖'})

        # Lưu tin nhắn người dùng
        ChatMessage.objects.create(nguoi_dung=request.user, message=message, is_bot=False)

        # Lấy lịch sử
        history = ChatMessage.objects.filter(nguoi_dung=request.user).order_by('-ngay_tao')[:500]
        history_context = "\n".join([
            f"{'User' if not msg.is_bot else 'Trợ lý'}: {msg.message}"
            for msg in reversed(history)
        ])

        try:
            response_text = get_gemini_response(request, message, history_context)
        except Exception as e:
            print("Gemini API Error:", str(e))
            response_text = get_smart_fallback(request, message)

        # Lưu tin nhắn bot
        ChatMessage.objects.create(nguoi_dung=request.user, message=response_text, is_bot=True)
        
        return JsonResponse({'response': response_text})

    # GET: Load lịch sử
    history = ChatMessage.objects.filter(nguoi_dung=request.user).order_by('ngay_tao')[:20]
    history_data = [{'message': msg.message, 'is_bot': msg.is_bot} for msg in history]
    return JsonResponse({'history': history_data})


def get_gemini_response(request, user_message, history_context=""):
    user = request.user
    recent_orders = DonHang.objects.filter(nguoi_dung=user).order_by('-ngay_dat')[:3]
    order_info = "Đơn hàng gần đây: " + ", ".join([f"#{o.id}" for o in recent_orders]) if recent_orders else "Chưa có đơn hàng"

    system_prompt = f"""Bạn là Trợ lý thời trang vui vẻ của OutfitLab. Trả lời bằng tiếng Việt, gần gũi, dùng emoji.

**Thông tin khách hàng:**
- Tên: {user.ho_ten or user.username}
- Hạng: {user.hang_thanh_vien}
- Chiều cao: {user.chieu_cao or 'chưa có'}cm
- Cân nặng: {user.can_nang or 'chưa có'}kg
- {order_info}

**Lịch sử hội thoại:**
{history_context}"""

    response = model.generate_content([system_prompt, user_message])
    return response.text.strip()


def get_smart_fallback(request, message):
    msg = message.lower().strip()
    if any(k in msg for k in ['đơn', 'lịch sử', 'order', '#']):
        return "📦 Bạn muốn xem đơn hàng gần nhất phải không? Cho mình số đơn hoặc mình sẽ liệt kê giúp."
    if any(k in msg for k in ['phối', 'outfit', 'mặc gì']):
        return "👗 Mình gợi ý áo thun basic phối quần jeans là đẹp nhất! Bạn thích phong cách nào?"
    if any(k in msg for k in ['size', 'form']):
        return "📏 Cho mình biết chiều cao cân nặng để mình tư vấn size chính xác hơn nhé!"
    return "💡 Mình là Stylist AI. Bạn cần tư vấn phối đồ, size, hay tra cứu đơn hàng?"

# ====================== OUTFIT AI - PHỐI ĐỒ THÔNG MINH ======================
@login_required
def phoi_do_ai(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        chieu_cao = float(data.get('chieu_cao', 170))
        can_nang = float(data.get('can_nang', 65))
        gioi_tinh = data.get('gioi_tinh', 'nam')
        dang_nguoi = data.get('dang_nguoi', '')
        mau_da = data.get('mau_da', 'trang')
        dip = data.get('dip', 'casual')
        phong_cach = data.get('phong_cach', 'casual')

        user = request.user
        is_female = gioi_tinh == 'nu'

        # ====================== PROMPT CHI TIẾT CHO GEMINI ======================
        system_prompt = f"""Bạn là Outfit AI chuyên nghiệp, sáng tạo và hiểu biết của OutfitLab.

Hãy tạo **một bộ outfit hoàn chỉnh, phù hợp nhất** dựa trên thông tin sau:

**Thông tin khách hàng:**
- Giới tính: {'Nữ' if is_female else 'Nam'}
- Chiều cao: {chieu_cao}cm, Cân nặng: {can_nang}kg
- Dáng người: {dang_nguoi or 'không xác định'}
- Màu da: {mau_da}
- Dịp mặc: {dip}
- Phong cách: {phong_cach}

**Yêu cầu:**
- Tôn trọng giới tính tuyệt đối.
- Gợi ý cụ thể, dễ mua.
- Trả về **CHỈ JSON** đúng format sau:

{{
  "description": "Mô tả tổng thể outfit chi tiết và cá nhân hóa (6-8 câu)",
  "color_harmony": "Gợi ý phối màu phù hợp",
  "items": [
    {{"ten": "Tên món đồ cụ thể", "category": "ao", "ly_do": "Lý do phù hợp..."}},
    {{"ten": "Tên món đồ cụ thể", "category": "quan", "ly_do": "Lý do phù hợp..."}},
    {{"ten": "Tên món đồ cụ thể", "category": "giay", "ly_do": "Lý do phù hợp..."}},
    {{"ten": "Tên món đồ cụ thể", "category": "phu_kien", "ly_do": "Lý do phù hợp..."}}
  ],
  "tips": "Mẹo phối đồ và lưu ý thực tế"
}}"""

        # ====================== GỌI GEMINI ======================
        outfit_data = None
        try:
            response = model.generate_content([system_prompt])
            gemini_text = response.text.strip()

            # Tìm và parse JSON
            if '{' in gemini_text:
                start = gemini_text.find('{')
                json_str = gemini_text[start:]
                outfit_data = json.loads(json_str)
        except Exception as e:
            print("Gemini API Error:", str(e))

        # ====================== FALLBACK TỐT HƠN ======================
        if not outfit_data or not outfit_data.get("items"):
            outfit_data = {
                "description": f"Outfit phù hợp với thông tin bạn cung cấp ({chieu_cao}cm - {can_nang}kg, phong cách {phong_cach}).",
                "color_harmony": "Tone màu trung tính dễ phối",
                "items": [
                    {"ten": "Áo thun basic oversize", "category": "ao", "ly_do": "Thoải mái, dễ phối đồ"},
                    {"ten": "Quần jeans ống rộng", "category": "quan", "ly_do": "Phong cách casual hiện đại"},
                    {"ten": "Giày sneaker trắng", "category": "giay", "ly_do": "Phù hợp mọi outfit"},
                    {"ten": "Mũ lưỡi trai hoặc túi đeo chéo", "category": "phu_kien", "ly_do": "Hoàn thiện outfit"}
                ],
                "tips": "Bạn có thể phối thêm phụ kiện để tăng cá tính."
            }

        # ====================== SẢN PHẨM TỪ SHOP ======================
        products_qs = SanPham.objects.filter(
            gioi_tinh__in=[gioi_tinh, 'unisex']
        ).prefetch_related('bien_the')

        final_products = []
        for cat, limit in [('ao', 5), ('quan', 4), ('phu_kien', 4)]:
            items = list(products_qs.filter(loai_san_pham=cat)[:limit])
            for sp in items:
                bien_the = sp.bien_the.first()
                if bien_the and not any(p.get('id') == sp.id for p in final_products):
                    final_products.append({
                        "id": sp.id,
                        "ten": sp.ten_san_pham[:70],
                        "gia": float(bien_the.gia),
                        "image": sp.hinh_anh.url if sp.hinh_anh else "/static/images/default-product.jpg",
                        "category": sp.loai_san_pham
                    })

        # Fallback nếu ít sản phẩm
        if len(final_products) < 6:
            extra = list(SanPham.objects.filter(
                gioi_tinh__in=[gioi_tinh, 'unisex']
            ).prefetch_related('bien_the').order_by('?')[:10])
            for sp in extra:
                if not any(p.get('id') == sp.id for p in final_products):
                    bien_the = sp.bien_the.first()
                    if bien_the:
                        final_products.append({
                            "id": sp.id,
                            "ten": sp.ten_san_pham[:70],
                            "gia": float(bien_the.gia),
                            "image": sp.hinh_anh.url if sp.hinh_anh else "/static/images/default-product.jpg",
                            "category": sp.loai_san_pham
                        })

        return JsonResponse({
            "success": True,
            "description": outfit_data.get("description", ""),
            "color_harmony": outfit_data.get("color_harmony", ""),
            "items": outfit_data.get("items", []),
            "tips": outfit_data.get("tips", ""),
            "products": final_products[:12]
        })

    except Exception as e:
        print("Outfit AI Error:", str(e))
        return JsonResponse({
            "success": False,
            "error": "Có lỗi khi tạo outfit. Vui lòng thử lại!"
        }, status=500)

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "Bạn không có quyền truy cập trang quản trị!")
        return redirect('trang_chu')

    # Lọc theo thời gian
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    don_qs = DonHang.objects.all()
    if start_date:
        don_qs = don_qs.filter(ngay_dat__date__gte=start_date)
    if end_date:
        don_qs = don_qs.filter(ngay_dat__date__lte=end_date)

    # ====================== TỔNG QUAN ======================
    total_customers = NguoiDung.objects.count()
    total_products = SanPham.objects.count()
    total_orders = don_qs.count()
    total_revenue = don_qs.aggregate(Sum('tong_tien'))['tong_tien__sum'] or 0

    # ====================== DOANH THU THEO NGÀY ======================
    revenue_qs = don_qs.annotate(date=TruncDate('ngay_dat')).values('date').annotate(
        total=Sum('tong_tien')
    ).order_by('date')[:30]
    
    revenue_labels = []
    revenue_values = []
    for d in revenue_qs:
        if d.get('date'):
            revenue_labels.append(d['date'].strftime('%d/%m'))
            revenue_values.append(float(d['total'] or 0))

    # FALLBACK nếu không có dữ liệu
    if not revenue_labels:
        recent_orders = don_qs.order_by('-ngay_dat')[:7]
        for order in recent_orders:
            revenue_labels.append(order.ngay_dat.strftime('%d/%m'))
            revenue_values.append(float(order.tong_tien or 0))
        
        if not revenue_labels:  # Vẫn không có
            revenue_labels = ["Chưa có đơn hàng"]
            revenue_values = [0]

    # ====================== TRẠNG THÁI ĐƠN HÀNG ======================
    status_data = don_qs.values('trang_thai').annotate(count=Count('id'))
    status_labels = []
    status_counts = []
    for s in status_data:
        status_labels.append(dict(DonHang.TRANG_THAI_CHOICES).get(s['trang_thai'], s['trang_thai']))
        status_counts.append(s['count'])

    if not status_labels:
        status_labels = ["Chưa có đơn"]
        status_counts = [0]

    # ====================== TOP SẢN PHẨM ======================
    top_products = SanPham.objects.annotate(
        so_luong_ban=Count('chitietdonhang'),
        doanh_thu=Sum('chitietdonhang__gia')
    ).order_by('-so_luong_ban')[:10]

    # ====================== DOANH THU THEO DANH MỤC ======================
    category_revenue = DanhMuc.objects.annotate(
        revenue=Sum('san_pham__chitietdonhang__gia', 
                   filter=Q(san_pham__chitietdonhang__don_hang__in=don_qs))
    ).order_by('-revenue')[:8]
    category_labels = [c.ten_danh_muc for c in category_revenue]
    category_values = [float(c.revenue or 0) for c in category_revenue]

    # ====================== TOP KHÁCH HÀNG ======================
    top_customers = DonHang.objects.values('nguoi_dung').annotate(
        so_don=Count('id'),
        tong_chi=Sum('tong_tien')
    ).order_by('-tong_chi')[:5]
    for tc in top_customers:
        try:
            tc['nguoi_dung'] = NguoiDung.objects.get(pk=tc['nguoi_dung'])
        except:
            tc['nguoi_dung'] = None

    # ====================== TỒN KHO & ĐƠN MỚI ======================
    low_stock = SanPhamBienThe.objects.filter(so_luong__lte=10).select_related('san_pham')[:10]
    recent_orders = don_qs.order_by('-ngay_dat')[:10]

    # ====================== CONTEXT ======================
    context = {
        'total_customers': total_customers,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'revenue_labels': json.dumps(revenue_labels),
        'revenue_data': json.dumps(revenue_values),
        'status_labels': json.dumps(status_labels),
        'status_data': json.dumps(status_counts),
        'top_products': top_products,
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_values),
        'top_customers': top_customers,
        'low_stock': low_stock,
        'recent_orders': recent_orders,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'admin_dashboard.html', context) 