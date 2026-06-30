from django import forms
from .models import NguoiDung, YeuCauHoanTien   # ← Đã thêm YeuCauHoanTien


class ProfileForm(forms.ModelForm):
    class Meta:
        model = NguoiDung
        fields = ['ho_ten', 'email', 'so_dien_thoai', 'dia_chi', 'chieu_cao', 'can_nang', 'so_thich', 'avatar']
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class YeuCauHoanTienForm(forms.ModelForm):
    class Meta:
        model = YeuCauHoanTien
        fields = ['ly_do', 'mo_ta', 'hinh_anh']
        widgets = {
            'mo_ta': forms.Textarea(attrs={
                'rows': 5, 
                'placeholder': 'Mô tả chi tiết vấn đề bạn gặp phải... (không bắt buộc)',
                'class': 'form-control'
            }),
            'hinh_anh': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }