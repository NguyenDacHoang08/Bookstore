# Hướng dẫn sử dụng BookStore với giao diện mới

## Bước 1: Khởi động tất cả các service

### Cách 1: Sử dụng script tự động (Khuyến nghị)
```bash
start_all_services.bat
```

Script này sẽ tự động khởi động tất cả 11 microservices và API Gateway.

### Cách 2: Khởi động thủ công
Mở 12 terminal/cmd riêng biệt và chạy:

```bash
# Terminal 1 - Customer Service
cd customer-service/customer_service
python manage.py runserver 8001

# Terminal 2 - Book Service
cd book-service/book_service
python manage.py runserver 8002

# Terminal 3 - Cart Service
cd cart-service/cart_service
python manage.py runserver 8003

# Terminal 4 - Staff Service
cd staff-service/staff_service
python manage.py runserver 8004

# Terminal 5 - Manager Service
cd manager-service/manager_service
python manage.py runserver 8005

# Terminal 6 - Catalog Service
cd catalog-service/catalog_service
python manage.py runserver 8006

# Terminal 7 - Order Service
cd order-service/order_service
python manage.py runserver 8007

# Terminal 8 - Ship Service
cd ship-service/ship_service
python manage.py runserver 8008

# Terminal 9 - Pay Service
cd pay-service/pay_service
python manage.py runserver 8009

# Terminal 10 - Comment Rate Service
cd comment-rate-service/comment_rate_service
python manage.py runserver 8010

# Terminal 11 - Recommend AI Service
cd recommend-ai-service/recommend_ai_service
python manage.py runserver 8011

# Terminal 12 - API Gateway
cd api-gateway
python manage.py runserver 8000
```

## Bước 2: Seed dữ liệu mẫu (có ảnh)

Sau khi tất cả services đã chạy, seed dữ liệu:

```bash
python scripts/seed_sample.py
```

Script này sẽ tạo:
- 10 cuốn sách với ảnh bìa đẹp
- 2 khách hàng (Alice, Bao)
- 1 staff
- Giỏ hàng mẫu
- Đánh giá mẫu
- 1 đơn hàng mẫu

## Bước 3: Truy cập giao diện

Mở trình duyệt và truy cập:
```
http://localhost:8000
```

## Tài khoản đăng nhập

### Khách hàng
- Email: `alice@example.com`
- Password: `password123`

hoặc

- Email: `bao@example.com`
- Password: `password123`

### Staff (Quản lý sách)
- Email: `staff@example.com`
- Password: `staff123`

## Tính năng giao diện mới

### 1. Trang chủ
- Hiển thị tất cả sách với ảnh bìa đẹp
- Card hiện đại với hover effect
- Tìm kiếm và lọc theo tác giả
- Thêm vào giỏ hàng trực tiếp
- Responsive trên mọi thiết bị

### 2. Chi tiết sách
- Ảnh sách lớn bên trái
- Thông tin chi tiết bên phải
- Form đánh giá và bình luận
- Hiển thị đánh giá từ khách hàng khác
- Sách gợi ý với ảnh

### 3. Giỏ hàng
- Hiển thị ảnh thumbnail cho mỗi sản phẩm
- Cập nhật số lượng
- Xóa sản phẩm
- Tính tổng tiền tự động

### 4. Thanh toán
- Xác nhận đơn hàng với ảnh
- Chọn phương thức thanh toán
- Chọn phương thức vận chuyển
- Nhập địa chỉ giao hàng

### 5. Quản lý sách (Staff)
- Xem danh sách sách với ảnh
- Thêm sách mới với URL ảnh
- Cập nhật thông tin sách (bao gồm ảnh)
- Xóa sách

## Thêm ảnh cho sách

### Nguồn ảnh miễn phí

1. **Open Library Covers API**
   ```
   https://covers.openlibrary.org/b/id/[ID]-L.jpg
   ```

2. **Amazon Images** (từ seed_sample.py)
   ```
   https://images-na.ssl-images-amazon.com/images/P/[ISBN].01.L.jpg
   ```

3. **Unsplash** (ảnh chất lượng cao)
   ```
   https://images.unsplash.com/photo-[ID]
   ```

4. **Google Books API**
   - Tìm sách trên Google Books
   - Lấy URL ảnh từ API

### Cách thêm ảnh qua giao diện Staff

1. Đăng nhập với tài khoản staff
2. Vào "Quản lý sách"
3. Khi thêm sách mới:
   - Điền đầy đủ thông tin
   - Paste URL ảnh vào trường "URL ảnh"
   - Click "Lưu"

4. Khi cập nhật sách:
   - Tìm sách trong danh sách
   - Sửa trường "URL ảnh"
   - Click "Cập nhật"

### Ví dụ URL ảnh từ seed_sample.py

```
https://images-na.ssl-images-amazon.com/images/P/B08K2XZPPZ.01.L.jpg
https://images-na.ssl-images-amazon.com/images/P/0735211299.01.L.jpg
https://images-na.ssl-images-amazon.com/images/P/0807014312.01.L.jpg
```

## Tính năng nổi bật

✅ Hiển thị ảnh sách ở mọi trang
✅ Giao diện hiện đại, responsive
✅ Hover effects mượt mà
✅ Placeholder đẹp khi không có ảnh
✅ Typography chuyên nghiệp
✅ Màu sắc hài hòa
✅ Tối ưu cho mobile
✅ Dễ sử dụng và trực quan

## Xử lý sự cố

### Services không khởi động
- Kiểm tra port đã bị chiếm chưa
- Đảm bảo đã cài đặt dependencies: `pip install -r requirements.txt`
- Kiểm tra database migrations đã chạy chưa

### Ảnh không hiển thị
- Kiểm tra URL ảnh có hợp lệ không
- Thử mở URL ảnh trực tiếp trên trình duyệt
- Đảm bảo URL bắt đầu bằng `http://` hoặc `https://`
- Một số nguồn ảnh có thể chặn hotlinking

### Seed data thất bại
- Đảm bảo tất cả services đã chạy
- Chờ 10-15 giây sau khi khởi động services
- Chạy lại script seed

## Tips

1. **Tìm ảnh sách nhanh**: Google "[Tên sách] book cover" và lấy URL ảnh
2. **Ảnh chất lượng tốt**: Nên dùng ảnh có kích thước tối thiểu 300x450px
3. **Tỷ lệ ảnh**: Ảnh bìa sách thường có tỷ lệ 2:3 (width:height)
4. **Performance**: URL ảnh từ CDN sẽ load nhanh hơn

## Liên hệ hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra console log trong browser (F12)
2. Kiểm tra terminal logs của các services
3. Đọc file GIAO_DIEN_MOI.md để hiểu chi tiết kỹ thuật
