# cuahang/resources.py
from import_export import resources
from .models import SanPham

class SanPhamResource(resources.ModelResource):
    class Meta:
        model = SanPham
        fields = ('id', 'ten_san_pham', 'danh_muc', 'loai_san_pham', 'gioi_tinh', 
                 'phong_cach', 'mo_ta', 'tags_phoi_do')
        export_order = ('id', 'ten_san_pham', 'danh_muc', ...)