from django.shortcuts import render,redirect,get_object_or_404
from .models import dmsanpham,sanpham,nhacc,khachhang,loaithetv,capnhatthe,khuyenmai,nhanvien,hinhanhsp,hoadon,tknhanvien,tkkhachhang,chitiethoadon
from .models import Cart,Cart_SP
from django.views.decorators.http import require_POST
from django.template import loader
from django.contrib import messages
from django.db.models import Max,Q,Count,F
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse,JsonResponse
from django.db import transaction
import os
from datetime import datetime,date,timedelta
from django.conf import settings
from django.utils.timezone import now
from django.utils import timezone
import logging,random

logger = logging.getLogger(__name__)

def index(request):
    
    sanphams = sanpham.objects.all().order_by('masp')
    dsdm = dmsanpham.objects.all()

    for sp in sanphams:
        sp.gia_khuyenmai = None
        if sp.makm:  # nếu có khuyến mãi
            giamgia = sp.makm.giamgia  # % giảm giá
            sp.gia_khuyenmai = sp.gia1dv * (1 - giamgia / 100)

    return render(request, 'User/index.html', {'sanphams': sanphams, 'dsdm': dsdm})

def SortSanPhamTheoDM(request, madm):
    sanphams = sanpham.objects.filter(madm=madm).order_by('masp')
    dsdm = dmsanpham.objects.all()

    for sp in sanphams:
        sp.gia_khuyenmai = None
        if sp.makm:  # nếu có khuyến mãi
            giamgia = sp.makm.giamgia  # % giảm giá
            sp.gia_khuyenmai = sp.gia1dv * (1 - giamgia / 100)

    return render(request, 'User/SortSanPhamTheoDM.html', {'sanphams': sanphams, 'dsdm': dsdm})

def chitietsanpham(request, masp):
    sp = get_object_or_404(sanpham, masp=masp)
    dsdm = dmsanpham.objects.all()
    

    folder = os.path.join(settings.BASE_DIR, "static", "HinhAnh", f"Hình {sp.masp}")
    thumbnails = []

    # Kiểm tra hình phụ tồn tại
    for i in range(2, 5):
        path = os.path.join(folder, f"HINH{i}.jfif")
        if os.path.exists(path):
            thumbnails.append(f"/static/HinhAnh/Hình {sp.masp}/HINH{i}.jfif")

    context = {
        "sp": sp,
        "main_image": f"/static/HinhAnh/Hình {sp.masp}/HINH1.jfif",
        "thumbnails": thumbnails,
        "dsdm": dsdm,
    }
    return render(request, "User/ChiTietSanPham.html", context)

def trang_san_pham(request):
    sort = request.GET.get('sort')
    sanphams = sanpham.objects.all().order_by('masp')
    dsdm = dmsanpham.objects.all()

    # Sắp xếp nếu có chọn
    if sort:
        sanphams = sanphams.order_by(sort)

    context = {
        'sanphams': sanphams,
        'dsdm' : dsdm,
    }
    return render(request, 'User/SanPham.html', context)

def search(request):
    search_term = request.GET.get('searchTerm', '').strip()
    dsdm = dmsanpham.objects.all()
    dssp = sanpham.objects.all()

    if search_term:
        dssp = dssp.filter(tensp__icontains=search_term)

    # gắn thêm thuộc tính giá khuyến mãi cho từng sản phẩm
    for sp in dssp:
        sp.gia_khuyenmai = None
        if sp.makm:  # nếu có khuyến mãi
            giamgia = sp.makm.giamgia  # % giảm giá
            sp.gia_khuyenmai = sp.gia1dv * (1 - giamgia / 100)

    return render(request, 'User/Search.html', {
        'dssp': dssp,
        'dsdm': dsdm,
        'search_term': search_term
    })


def KhuyenMai(request):
    # Lấy tất cả sản phẩm có mã khuyến mãi
    sanphams = sanpham.objects.filter(makm__isnull=False)

    # Thêm field tạm: giá khuyến mãi
    for sp in sanphams:
        sp.gia_khuyenmai = sp.gia1dv * (1 - sp.makm.giamgia / 100)

    dsdm = dmsanpham.objects.all()
    return render(request, "User/KhuyenMai.html", {
        "sanphams": sanphams,
        "dsdm": dsdm
    })


#######################Xử lý thông báo chung#########################

def my_view(request):
    # Ví dụ thêm lỗi
    if some_error_condition:
        messages.error(request, "Có lỗi xảy ra!")
        return redirect("index")

    # Ví dụ thêm thành công
    messages.success(request, "Thao tác thành công!")
    return redirect("index")


def add_to_cart(request):
    # Nếu có lỗi giỏ hàng
    messages.error(request, "Giỏ hàng có lỗi!")
    return redirect("cart")

def checkout(request):
    # Nếu thanh toán thành công
    messages.success(request, "Thanh toán thành công!")
    return redirect("index")


###############################       DANG KY - DANG NHAP - DANG XUAT       ############################################

# GET: hiển thị form đăng ký
def dangky(request):
    if request.method == "GET":
        return render(request, "User/DangKy.html")

    # POST: xử lý dữ liệu đăng ký
    if request.method == "POST":
        tenkhachhang = request.POST.get("tenkhachhang")
        username = request.POST.get("Username")
        sdt = request.POST.get("sdt")
        address = request.POST.get("address")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        # Kiểm tra mật khẩu xác nhận
        if password != confirm:
            messages.error(request, "Mật khẩu và xác nhận mật khẩu không khớp.")
            return redirect("dangky")

        # Kiểm tra tài khoản tồn tại chưa
        tk = "TK_" + username
        if tkkhachhang.objects.filter(tentkkh=tk).exists():
            messages.error(request, "Tài khoản đã tồn tại.")
            return redirect("dangky")

        # Sinh mã khách hàng tự động
        last_customer = khachhang.objects.aggregate(Max("makh"))["makh__max"]
        if last_customer:
            last_num = int(last_customer[2:])  # bỏ "KH"
            new_makh = f"KH{last_num+1:03d}"
        else:
            new_makh = "KH000"

        # Kiểm tra khách hàng theo số điện thoại
        customer, created = khachhang.objects.get_or_create(
            sdt=sdt,
            defaults={
                "makh": new_makh,
                "tenkh": tenkhachhang,
                "diachi": address,
                "capdotv": "Đồng",  # mặc định cấp độ thẻ
            },
        )

        # Nếu khách hàng chưa tạo thành công
        if not customer:
            messages.error(request, "Có lỗi khi tạo khách hàng mới.")
            return redirect("dangky")

        # Tạo tài khoản mới
        new_account = tkkhachhang(
            tentkkh=tk,
            makh=customer.makh,
            matkhau=password
        )
        new_account.save()

        # Kiểm tra tài khoản có lưu được không
        if not tkkhachhang.objects.filter(tentkkh=new_account.tentkkh).exists():
            messages.error(request, "Tạo tài khoản không thành công.")
            return redirect("dangky")

        # Cập nhật thẻ thành viên
        card_update = capnhatthe(
            makh=customer.makh,
            maloithe="T01",  # mã thẻ mặc định
            ngaycapnhat=timezone.now()
        )
        card_update.save()

        # Lưu thông báo thành công
        messages.success(request, "Đăng ký thành công. Vui lòng đăng nhập.")
        request.session["Username"] = new_account.tentkkh
        request.session["Password"] = new_account.matkhau

        return redirect("dangky")

# Đăng xuất

def dangxuat(request):
    # Xóa toàn bộ session
    request.session.flush()

    # Nếu chỉ muốn xoá 1 số key thì làm thế này:
    # for key in ["IsAuthenticated", "Username", "MaKH", "Name", "IsAdmin"]:
    #     request.session.pop(key, None)

    messages.success(request, "Cảm ơn khách hàng đã mua hàng!")  # giống TempData

    return redirect("index")  # quay về trang chủ


# GET: hiển thị form đăng nhập

def dangnhap(request):

    if request.method == "GET":
        return render(request, "User/DangNhap.html")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Kiểm tra khách hàng
        account = tkkhachhang.objects.filter(tentk=username).first()
        admin = tknhanvien.objects.filter(tentk=username).first()

        if account:
            if account.matkhau == password:  # ❗ Nên hash để bảo mật
                # Lưu session (chỉ lưu string hoặc int, không lưu object)
                request.session["IsAuthenticated"] = True
                request.session["Username"] = account.tentk
                request.session["MaKH"] = str(account.makh_id)

                # Lấy thêm thông tin khách hàng
                kh = khachhang.objects.filter(makh=account.makh).first()
                if kh:
                    request.session["Name"] = kh.tenkh

                messages.success(request, f"Xin chào {request.session['Name']}!")
                return redirect("index")  # Trang chủ
            else:
                messages.error(request, "Tài khoản hoặc mật khẩu không đúng")
                return redirect("dangnhap")

        elif admin:
            # Đăng nhập admin
            request.session["IsAdmin"] = True
            request.session["Username"] = admin.tentk
            request.session["IsAuthenticated"] = True
            return redirect("quanli_index")  # Trang quản lý (admin)

        else:
            messages.error(request, "Tài khoản không tồn tại, vui lòng đăng ký")
            return redirect("dangnhap")

##################################GIO HANG - THANH TOAN#######################################

# ------------------------------
# Mở giỏ hàng
# ------------------------------
def open_cart(request):
    #if not request.session.get("IsAuthenticated"):
    #    request.session["error_cart"] = "Vui lòng đăng nhập để vào giỏ hàng."
    #    return redirect("index")

    cart_data = request.session.get("cart")
    cart = Cart.from_dict(cart_data) if cart_data else Cart()
    return render(request, "User/OpenCart.html", {"cart": cart})




# ------------------------------
# Cập nhật số lượng
# ------------------------------
@require_POST
def update_quantity(request, masp):
    # Lấy số lượng thay đổi từ form
    delta = int(request.POST.get("quantityChange", 0))

    # Lấy giỏ hàng từ session
    cart_data = request.session.get("cart")
    if not cart_data:
        messages.error(request, "Giỏ hàng trống.")
        return redirect("opencart")

    # Tạo Cart object từ session
    cart = Cart.from_dict(cart_data)

    # Cập nhật số lượng
    cart.cap_nhat_sl(masp, delta)

    # Lưu lại vào session
    request.session["cart"] = cart.to_dict()
    request.session.modified = True

    # Quay lại trang giỏ hàng
    return redirect("opencart")



# ------------------------------
# Xóa sản phẩm khỏi giỏ
# ------------------------------
def remove_from_cart(request, product_id):
    cart_data = request.session.get("cart")
    cart = Cart.from_dict(cart_data) if cart_data else Cart()

    cart.xoa_sp(product_id)
    request.session["cart"] = cart.to_dict()
    request.session.modified = True

    return redirect("opencart")

@require_POST
def gio_hang(request):
    # 🟡 1. Lấy dữ liệu từ form
    product_id = request.POST.get("productId")
    quantity = int(request.POST.get("quantity", 1))

    # 🟡 2. Kiểm tra trạng thái đăng nhập
    #if not request.session.get("IsAuthenticated"):
    #    messages.error(request, "Vui lòng đăng nhập trước khi thêm sản phẩm vào giỏ hàng.")
    #    return redirect("chitietsanpham", masp=product_id)

    # 🟡 3. Kiểm tra tham số đầu vào
    if not product_id or quantity <= 0:
        messages.error(request, "Dữ liệu không hợp lệ.")
        return redirect("error_page")

     # Lấy sản phẩm từ database
    sp_instance = get_object_or_404(sanpham, masp=product_id)

    # Kiểm tra tồn kho trước khi thêm vào giỏ
    if sp_instance.soluongtk == 0:
        messages.error(request, f"Sản phẩm '{sp_instance.tensp}' đang hết hàng, không thể thêm vào giỏ.")
        return redirect("chitietsanpham", masp=product_id)

    

    # 🟡 4. Lấy giỏ hàng từ session (nếu chưa có thì khởi tạo mới)
    cart_data = request.session.get("cart")
    cart = Cart()  # Lớp Cart bạn đã định nghĩa trong models hoặc 1 file riêng

    if cart_data:
        # khôi phục dữ liệu giỏ hàng từ session
        for sp_data in cart_data["listSP"]:
            sp = Cart_SP(sp_data["masanpham"])
            sp.soluong = sp_data["soluong"]
            cart.listSP.append(sp)

    # 🟡 5. Thêm sản phẩm vào giỏ
    cart.them_sp(product_id, quantity)

    # 🟡 6. Lưu lại giỏ hàng vào session
    request.session["cart"] = cart.to_dict()
    request.session.modified = True

    # 🟡 7. Thông báo cho người dùng
    messages.success(request, f"Đã thêm {quantity} sản phẩm '{sp_instance.tensp}' vào giỏ hàng.")

    # 🟡 8. Quay lại trang chi tiết sản phẩm
    return redirect("chitietsanpham", masp=product_id)

##################################LIEN HE#######################################
def lienhe(request):
    return render(request, "User/LienHe.html")


#################################THANH TOAN - DAT HANG##################################3


def thanh_toan(request):
    # ✅ Lấy giỏ hàng từ session
    cart = request.session.get('cart', None)

    if not cart or len(cart.get('listSP', [])) == 0:
        messages.error(request, "Giỏ hàng của bạn không có sản phẩm. Vui lòng thêm sản phẩm vào giỏ hàng trước khi thanh toán.")
        return redirect('opencart')

    # ✅ Lấy khách hàng đăng nhập (nếu có)
    ma_kh = request.session.get('MaKH', None)
    khach = khachhang.objects.filter(makh=ma_kh).first() if ma_kh else None

    # ✅ Lấy khuyến mãi (nếu có)
    km = khuyenmai.objects.first()
    giamgia = km.giamgia if km else 0

    tong_tien_goc = 0
    gio_hang_hop_le = True  # cờ kiểm tra nếu có sản phẩm hết hàng

    for sp in cart['listSP']:
        try:
            sp_db = sanpham.objects.get(masp=sp['masanpham'])
            sp['tensp'] = sp_db.tensp
            sp['gia_hientai'] = sp_db.gia_sau_km()
            sp['soluongton'] = sp_db.soluongtk
        except sanpham.DoesNotExist:
            sp['tensp'] = "Không tồn tại"
            sp['soluongton'] = 0

        soluong = int(sp.get('soluong', 0))
        giatien = int(sp.get('giatien', 0))
        sp['thanhtien'] = soluong * giatien
        tong_tien_goc += sp['thanhtien']

        # ✅ Kiểm tra hàng tồn
        if sp.get('soluongton', 0) <= 0:
            gio_hang_hop_le = False
            messages.warning(request, f"Sản phẩm '{sp['tensp']}' hiện đã hết hàng.")
        elif soluong > sp['soluongton']:
            gio_hang_hop_le = False
            messages.warning(request, f"Sản phẩm '{sp['tensp']}' chỉ còn {sp['soluongton']} sản phẩm trong kho.")

    # ✅ Nếu có sản phẩm lỗi => quay lại giỏ hàng
    if not gio_hang_hop_le:
        return redirect('gio_hang')

    # ✅ Tính tổng sau giảm giá (nếu có)
    tong_tien_sau_giam = int(tong_tien_goc * (1 - giamgia / 100)) if giamgia else tong_tien_goc

    context = {
        'cart': cart,
        'khach': khach,
        'giamgia': giamgia,
        'tong_tien_goc': tong_tien_goc,
        'tong_tien_sau_giam': tong_tien_sau_giam,
    }

    return render(request, 'User/ThanhToan.html', context)



@transaction.atomic
def dat_hang(request):
    if request.method == 'POST':
        ship_method = request.POST.get('shipMethod')
        payment_method = request.POST.get('payment_method')

        if not ship_method or not payment_method:
            messages.error(request, "Vui lòng chọn đầy đủ phương thức giao hàng và thanh toán.")
            return redirect('thanhtoan')

        cart = request.session.get('cart', {})
        if not cart or len(cart.get('listSP', [])) == 0:
            messages.error(request, "Giỏ hàng của bạn trống.")
            return redirect('gio_hang')

        # ✅ Lấy mã KH (nếu có)
        ma_kh = request.session.get('MaKH', None)
        khach = khachhang.objects.filter(makh=ma_kh).first() if ma_kh else None

        # ✅ Sinh mã hóa đơn
        last_hd = hoadon.objects.order_by('-mahd').first()
        last_index = int(last_hd.mahd[2:]) if last_hd else 0
        new_mahd = f"hd{last_index + 1:03d}"

        # ✅ Lấy khuyến mãi (nếu có)
        km = khuyenmai.objects.first()
        giamgia = km.giamgia if km else 0

        tongtien = sum(int(sp['giatien']) * int(sp['soluong']) for sp in cart['listSP'])
        if giamgia:
            tongtien = int(tongtien * (1 - giamgia / 100))

        ngay_giao = date.today() + timedelta(days=3)
        ds_nv = list(nhanvien.objects.all())
        nv_random = random.choice(ds_nv) if ds_nv else None

        # ✅ Tạo hóa đơn trước (tạm)
        new_hoadon = hoadon.objects.create(
            mahd=new_mahd,
            makh=khach,
            ngaydat=date.today(),
            trangthaihd="ĐANG CHỜ",
            phuongthucgh=ship_method,
            phuongthucthtoan=payment_method,
            ngaygiao=ngay_giao,
            manv=nv_random,
            makm=km,
            tongtien=tongtien
        )

        # ✅ Lấy danh sách sản phẩm và khóa chúng
        masp_list = [item['masanpham'] for item in cart['listSP']]
        sanphams = sanpham.objects.select_for_update().filter(masp__in=masp_list)

        # Tạo dictionary để truy nhanh
        sp_dict = {sp.masp: sp for sp in sanphams}

        # ✅ Sinh mã chi tiết hóa đơn
        last_cthd = chitiethoadon.objects.order_by('-macthd').first()
        last_index_ct = int(last_cthd.macthd[4:]) if last_cthd else 0

        for item in cart['listSP']:
            masp = item['masanpham']
            so_luong_mua = int(item['soluong'])
            sp_instance = sp_dict.get(masp)

            if not sp_instance:
                transaction.set_rollback(True)
                messages.error(request, f"Sản phẩm mã {masp} không tồn tại.")
                return redirect('gio_hang')

            # ✅ Kiểm tra tồn kho thật
            if sp_instance.soluongtk < so_luong_mua:
                transaction.set_rollback(True)
                messages.error(request, f"Sản phẩm '{sp_instance.tensp}' không đủ hàng trong kho.")
                return redirect('gio_hang')

            # ✅ Trừ tồn kho an toàn (bên trong transaction)
            sp_instance.soluongtk = F('soluongtk') - so_luong_mua
            sp_instance.save()

            last_index_ct += 1
            new_macthd = f"cthd{last_index_ct:03d}"

            # ✅ Tạo chi tiết hóa đơn
            chitiethoadon.objects.create(
                macthd=new_macthd,
                mahd=new_hoadon,
                masp=sp_instance,
                soluongban=so_luong_mua,
                giaban=item['giatien']
            )

        # ✅ Xóa giỏ hàng khỏi session sau khi đặt thành công
        if 'cart' in request.session:
            del request.session['cart']

        messages.success(request, "Đặt hàng thành công! Cảm ơn bạn đã mua sắm.")
        return redirect('index')

    return redirect('thanhtoan')



################################QUAN LI - ADMIN##############################################

def quanli_index(request):
    status = request.GET.get('status', '')  # lấy status từ query string ?status=...
    payment = request.GET.get('payment', '')  # lấy phương thức thanh toán từ query string
    hoadons = hoadon.objects.all()

    if status:
        hoadons = hoadons.filter(trangthaihd__iexact=status)  # so sánh không phân biệt hoa thường

    if payment:
        hoadons = hoadons.filter(phuongthucthanhtoan__iexact=payment)

    hoadons = hoadons.order_by('-mahd')  # sắp xếp giảm dần theo MAHD

    return render(request, 'QuanLi/QuanLi_Index.html', {'hoadons': hoadons})


def change_status(request):
    if request.method == 'POST':
        mahd = request.POST.get('mahd')
        change_status = request.POST.get('changeStatus')

        # Tìm hóa đơn theo MAHD
        hd = get_object_or_404(hoadon, mahd=mahd)

        if change_status == "ĐANG GIAO":
            # Lấy danh sách nhân viên và số đơn đã giao
            nhanviens = (
                nhanvien.objects
                .annotate(so_don_da_giao=Count('hoadon'))  # đếm số hóa đơn theo nhân viên
                .order_by('so_don_da_giao')
            )

            nhan_vien_giao_hang = nhanviens.first()
            if nhan_vien_giao_hang:
                hd.manv = nhan_vien_giao_hang  # Gán nhân viên giao hàng

        elif change_status == "HOÀN THÀNH":
            hd.ngaygiao = timezone.now()

        hd.trangthaihd = change_status
        hd.save()

        messages.success(request, "Trạng thái đơn hàng đã được cập nhật!")

    return redirect('quanli_index') 

def khuyenmai_quanli(request):
    dskm = khuyenmai.objects.all().order_by('-makm')
    return render(request, "QuanLi/KhuyenMai_QuanLi.html", {"dskm": dskm})


def them_km(request):
    if request.method == 'POST':
        tenKM = request.POST.get('tenKM')
        ngayBatDau = request.POST.get('ngayBatDau')
        ngayKetThuc = request.POST.get('ngayKetThuc')
        phanTramGiam = request.POST.get('phanTramGiam')

        # Kiểm tra dữ liệu đầu vào
        if not tenKM or not ngayBatDau or not ngayKetThuc or not phanTramGiam or int(phanTramGiam) <= 0:
            messages.error(request, "Vui lòng kiểm tra thông tin.")
            return render(request, 'QuanLi/ThemKM_QuanLi.html')

        # Tạo mã khuyến mãi tự động (tương đương Substring + tăng index)
        last_km = khuyenmai.objects.order_by('-makm').first()
        if last_km:
            last_index = int(last_km.makm[2:])  # cắt chuỗi "KMxxx"
        else:
            last_index = 0
        new_makm = f"KM{last_index + 1:03d}"

        # Tạo mới khuyến mãi
        km = khuyenmai(
            makm=new_makm,
            tenkm=tenKM,
            ngaybd=ngayBatDau,
            ngaykt=ngayKetThuc,
            giamgia=int(phanTramGiam)
        )
        km.save()

        messages.success(request, "Khuyến mãi mới đã được thêm vào danh sách.")
        return redirect('khuyenmai_quanli')  # chuyển hướng về trang danh sách KM

    # GET request
    return render(request, 'QuanLi/ThemKM_QuanLi.html')

def deleteKM(request):
    if request.method == 'POST':
        makm = request.POST.get('makm')
        try:
            km = khuyenmai.objects.get(makm=makm)
            km.delete()
            messages.success(request, "Xóa khuyến mãi thành công!")
        except khuyenmai.DoesNotExist:
            messages.error(request, "Không tìm thấy khuyến mãi cần xóa!")

    return redirect('khuyenmai_quanli') 

def thongkeHD(request):
    time_filter = request.GET.get('time', '')
    dshd = hoadon.objects.filter(trangthaihd="HOÀN THÀNH").order_by('-mahd')

    current_date = timezone.now().date()

    if time_filter:
        if time_filter == "Theo Ngày":
            dshd = dshd.filter(ngaydat__date=current_date)

        elif time_filter == "Theo Tuần":
            # Tính ngày bắt đầu và kết thúc tuần hiện tại
            start_of_week = current_date - timedelta(days=current_date.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            dshd = dshd.filter(ngaydat__date__gte=start_of_week, ngaydat__date__lte=end_of_week)

        elif time_filter == "Theo Tháng":
            dshd = dshd.filter(ngaydat__month=current_date.month, ngaydat__year=current_date.year)

        elif time_filter == "Theo Năm":
            dshd = dshd.filter(ngaydat__year=current_date.year)

    return render(request, 'QuanLi/ThongKeHD.html', {'dshd': dshd})

#####################################THÔNG TIN KHÁCH HÀNG - LỊCH SỬ MUA HÀNG##################33333
def thongtinKH(request):
    
    ma_kh = request.session.get('MaKH', None)
    khach = None
    if ma_kh:
        khach = khachhang.objects.filter(makh=ma_kh).first()

    return render(request,"User/ThongTinKH.html",{"khach":khach})
