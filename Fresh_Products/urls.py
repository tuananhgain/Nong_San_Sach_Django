from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path("sort/<str:madm>/", views.SortSanPhamTheoDM, name="SortSanPhamTheoDM"),
    path('search/', views.search, name='search'),
    path('san-pham/', views.trang_san_pham, name='trang_san_pham'),
    path('sanpham/<str:masp>/', views.chitietsanpham, name='chitietsanpham'),
    path("khuyenmai/", views.KhuyenMai, name="khuyenmai"),
    path('dangky/', views.dangky, name='dangky'),
    path('dangnhap/', views.dangnhap, name='dangnhap'),
    path('dangxuat/', views.dangxuat, name='dangxuat'),
    path('opencart/', views.open_cart, name='opencart'),
    path('add_to_cart/<str:masp>/', views.add_to_cart, name='add_to_cart'),
    path('update_cart/<str:masp>/', views.update_quantity, name='update_quantity'),
    path('remove_from_cart/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('giohang/', views.gio_hang, name='gio_hang'),
    path('lienhe/', views.lienhe, name='lienhe'),
    path('thanhtoan/',views.thanh_toan, name='thanhtoan'),
    path('dathang/',views.dat_hang,name='dathang'),
    path('quanli_index/', views.quanli_index, name='quanli_index'),
    path('change_status/', views.change_status, name='change_status'),
    path('khuyenmai_quanli/', views.khuyenmai_quanli, name='khuyenmai_quanli'),
    path('Add_Discount/',views.them_km, name='ThemKM_QL'),
    path('Delete_Discount/',views.deleteKM, name='XoaKM_QL'),
    path('Manage_Orders/', views.thongkeHD, name='ThongKeHD_QL'),
    path('ThongtinKhachHang/',views.thongtinKH,name='thongtinKH')
]