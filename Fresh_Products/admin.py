from django.contrib import admin
from .models import dmsanpham,sanpham,nhacc,khachhang,loaithetv,capnhatthe,khuyenmai,nhanvien,hinhanhsp,hoadon,tknhanvien,tkkhachhang,chitiethoadon


# Register your models here.
class dmsanphamAdmin(admin.ModelAdmin):
    list_display = ("madm","tendm")
    ordering = ['madm']  # Sắp xếp theo trường 'madm' tăng dần

class sanphamAdmin(admin.ModelAdmin):
    list_display = ("masp","tensp","donvitinh","gia1dv","soluongtk","xuatxu","madm","mancc")
    ordering = ['masp']  # Sắp xếp theo trường 'masp' tăng dần

class nhaccAdmin(admin.ModelAdmin):
    list_display = ("mancc","tencc","diachi")
    ordering = ['mancc']  # Sắp xếp theo trường 'mancc' tăng dần

class khachhangAdmin(admin.ModelAdmin):
    list_display = ("makh","tenkh","diachi","sdt","capdotv")
    ordering = ['makh']  # Sắp xếp theo trường 'makh' tăng dần

class loaithetvAdmin(admin.ModelAdmin):
    list_display = ("maloaithe","tenthe","uudai","dieukien")
    ordering = ['maloaithe']  # Sắp xếp theo trường 'maloaithe' tăng dần

class capnhattheAdmin(admin.ModelAdmin):
    list_display = ("makh","maloaithe","ngaycap")
    ordering = ['makh']  # Sắp xếp theo trường 'makh' tăng dần

class khuyenmaiAdmin(admin.ModelAdmin):
    list_display = ("makm","tenkm","ngaybd","ngaykt","giamgia") 
    ordering = ['makm']  # Sắp xếp theo trường 'makm' tăng d

class nhanvienAdmin(admin.ModelAdmin):
    list_display = ("manv","tennv","diachi","gioitinh","cccd","sdt","ngaysinh","chucvu") 
    ordering = ['manv']  # Sắp xếp theo trường 'manv' tăng dần

class hinhanhspAdmin(admin.ModelAdmin):
    list_display = ("mahinh","tenhinh","masp")  
    ordering = ['mahinh']  # Sắp xếp theo trường 'mahinh' tăng dần

class hoadonAdmin(admin.ModelAdmin):
    list_display = ("mahd","makh","manv","makm","ngaydat","trangthaihd","phuongthucgh","phuongthucthtoan","ngaygiao","tongtien")   
    ordering = ['mahd']  # Sắp xếp theo trường 'mahd' tăng dần

class tknhanvienAdmin(admin.ModelAdmin):
    list_display = ("tentk","manv","matkhau")
    ordering = ['tentk']  # Sắp xếp theo trường 'tentk' tăng dần

class tkkhachhangAdmin(admin.ModelAdmin):
    list_display = ("tentk","makh","matkhau")
    ordering = ['tentk']  # Sắp xếp theo trường 'tentk' tăng dần

class chitiethoadonAdmin(admin.ModelAdmin):
    list_display = ("macthd","mahd","masp","soluongban","giaban")
    ordering = ['macthd']  # Sắp xếp theo trường 'macthd' tăng dần


admin.site.register(dmsanpham, dmsanphamAdmin)
admin.site.register(sanpham, sanphamAdmin)
admin.site.register(nhacc, nhaccAdmin)
admin.site.register(khachhang, khachhangAdmin)
admin.site.register(loaithetv, loaithetvAdmin)
admin.site.register(capnhatthe, capnhattheAdmin)
admin.site.register(khuyenmai, khuyenmaiAdmin)
admin.site.register(nhanvien, nhanvienAdmin)
admin.site.register(hinhanhsp, hinhanhspAdmin)
admin.site.register(hoadon, hoadonAdmin)
admin.site.register(tknhanvien, tknhanvienAdmin)
admin.site.register(tkkhachhang, tkkhachhangAdmin)
admin.site.register(chitiethoadon, chitiethoadonAdmin)
