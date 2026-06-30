from .models import DanhMuc

def menu_categories(request):
    """Truyền danh mục động theo giới tính"""
    all_danh_muc = DanhMuc.objects.all().order_by('ten_danh_muc')
    
    return {
        'danh_muc_nam': all_danh_muc.filter(gioi_tinh_hop_le__in=['nam', 'unisex']),
        'danh_muc_nu': all_danh_muc.filter(gioi_tinh_hop_le__in=['nu', 'unisex']),
        'danh_muc_unisex': all_danh_muc.filter(gioi_tinh_hop_le='unisex'),
    }