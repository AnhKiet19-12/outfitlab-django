from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout

class AdminStaffMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Chỉ áp dụng cho các trang Admin
        if request.path.startswith('/admin/'):
            if request.user.is_authenticated and not (request.user.is_staff or request.user.is_superuser):
                # Logout user thường và yêu cầu login lại bằng tài khoản Admin
                logout(request)
                messages.warning(request, 'Vui lòng đăng nhập bằng tài khoản Admin để truy cập trang quản trị.')
                return redirect(f'/admin/login/?next={request.path}')
        
        return self.get_response(request)