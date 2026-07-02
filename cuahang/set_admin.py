# -*- coding: utf-8 -*-
from cuahang.models import NguoiDung

def set_admin(username):
    try:
        user = NguoiDung.objects.get(username=username)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"✅ Đã cấp quyền Admin cho {user.username}")
        print(f"   Staff: {user.is_staff} | Superuser: {user.is_superuser}")
    except NguoiDung.DoesNotExist:
        print(f"❌ Không tìm thấy user với username: {username}")
    except Exception as e:
        print(f"❌ Lỗi: {e}")

# ====================== CHẠY TẠI ĐÂY ======================
if __name__ == "__main__":
    set_admin('admin')   # ← THAY TÊN USERNAME ADMIN CỦA BẠN VÀO ĐÂY