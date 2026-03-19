# Tối ưu giao diện BookStore - Hiển thị ảnh sách

## Các cải tiến đã thực hiện

### 1. Hiển thị ảnh sách trên tất cả các trang

#### Trang chủ (home.html)
- Card sách hiện đại với ảnh bìa lớn
- Hiệu ứng hover mượt mà
- Layout responsive với grid tự động điều chỉnh
- Badge hiển thị số lượng tồn kho
- Placeholder đẹp mắt khi không có ảnh

#### Trang chi tiết sách (book_detail.html)
- Ảnh sách lớn ở bên trái (max 400px)
- Thông tin chi tiết ở bên phải
- Phần sách gợi ý với ảnh thumbnail
- Form đánh giá và hiển thị đánh giá từ khách hàng

#### Giỏ hàng (cart.html)
- Hiển thị ảnh thumbnail (60x85px) cho mỗi sản phẩm
- Placeholder SVG đẹp mắt khi không có ảnh
- Layout table với ảnh và thông tin sách

#### Trang thanh toán (checkout.html)
- Hiển thị ảnh thumbnail (40x56px) trong bảng xác nhận đơn hàng
- Tổng quan đơn hàng trước khi đặt

#### Quản lý sách - Staff (staff_books.html)
- Cột ảnh trong bảng quản lý
- Form thêm/cập nhật có trường URL ảnh
- Preview ảnh thumbnail trong danh sách

### 2. Thiết kế giao diện mới

#### Màu sắc và Typography
- Font chữ: Manrope (body), Playfair Display (headings)
- Màu chủ đạo: #1f3b4d (brand), #e08f62 (accent)
- Background gradient tinh tế
- Border và shadow mềm mại

#### Components
- **Book Card**: Card hiện đại với ảnh, hover effect, badge
- **Book Image**: Aspect ratio 2:3, object-fit cover, border-radius
- **Placeholder**: SVG icon sách khi không có ảnh
- **Buttons**: Rounded, shadow, hover animations
- **Badges**: Soft colors, rounded pills

### 3. Responsive Design
- Mobile-first approach
- Grid tự động điều chỉnh: 1-4 cột tùy màn hình
- Touch-friendly buttons và inputs
- Optimized cho tablet và desktop

## Cách sử dụng

### Thêm ảnh cho sách

#### Qua giao diện Staff
1. Đăng nhập với tài khoản staff
2. Vào "Quản lý sách"
3. Khi thêm sách mới, điền URL ảnh vào trường "URL ảnh"
4. Hoặc cập nhật sách hiện có bằng cách sửa trường "URL ảnh"

#### Ví dụ URL ảnh
```
https://covers.openlibrary.org/b/id/8739161-L.jpg
https://images-na.ssl-images-amazon.com/images/I/51Ga5GuElyL._SX331_BO1,204,203,200_.jpg
https://m.media-amazon.com/images/I/71-++hbbERL._AC_UF1000,1000_QL80_.jpg
```

### Nguồn ảnh miễn phí
- **Open Library Covers API**: https://openlibrary.org/dev/docs/api/covers
- **Google Books API**: https://developers.google.com/books
- **Unsplash**: https://unsplash.com/s/photos/book
- **Pexels**: https://www.pexels.com/search/book/

## Cấu trúc CSS

### Các class chính
- `.book-card`: Container cho card sách
- `.book-image-link`: Link wrapper cho ảnh
- `.book-image`: Ảnh sách với object-fit
- `.book-image-placeholder`: Placeholder khi không có ảnh
- `.book-content`: Nội dung text của card
- `.book-title`, `.book-author`, `.book-price`: Typography
- `.book-actions`: Container cho buttons
- `.btn-add-cart`, `.btn-login`: Action buttons

### Responsive breakpoints
- Mobile: < 768px (1 column)
- Tablet: 768px - 1024px (2-3 columns)
- Desktop: > 1024px (3-4 columns)

## Tính năng nổi bật

1. **Lazy loading ready**: Ảnh có thể được lazy load
2. **SEO friendly**: Alt text cho tất cả ảnh
3. **Performance**: Optimized image sizes
4. **Accessibility**: Placeholder có ý nghĩa
5. **User experience**: Smooth transitions và hover effects

## Lưu ý kỹ thuật

- Model Book đã có trường `image_url` (URLField, blank=True, null=True)
- Views đã được cập nhật để xử lý image_url
- Template sử dụng `{% if book.image_url %}` để kiểm tra
- Placeholder SVG được inline để tránh request thêm
- CSS được tối ưu với CSS variables

## Tương lai

Có thể mở rộng:
- Upload ảnh trực tiếp thay vì URL
- Image optimization và CDN
- Multiple images per book
- Zoom ảnh khi click
- Image gallery cho sách
