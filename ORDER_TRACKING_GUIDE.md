# Hướng dẫn sử dụng tính năng theo dõi và duyệt đơn hàng

## Tổng quan

Đã thêm thành công các tính năng mới cho Order Service:

### 🔍 Tính năng theo dõi đơn hàng cho Customer
- Theo dõi trạng thái đơn hàng
- Xem thông tin vận chuyển
- Lịch sử đơn hàng

### ✅ Tính năng duyệt đơn hàng cho Staff
- Duyệt/từ chối đơn hàng
- Cập nhật thông tin theo dõi
- Quản lý trạng thái đơn hàng

## Các trường mới trong Order Model

```python
# Trường duyệt đơn hàng
approval_status = CharField(choices=['pending', 'approved', 'rejected'])
approved_by = IntegerField()  # staff_id
approved_at = DateTimeField()
rejection_reason = TextField()

# Trường theo dõi đơn hàng
tracking_number = CharField(max_length=100)
estimated_delivery = DateTimeField()
notes = TextField()
updated_at = DateTimeField(auto_now=True)

# Cập nhật trường status với nhiều lựa chọn hơn
status = CharField(choices=[
    'pending', 'processing', 'confirmed', 
    'shipped', 'delivered', 'cancelled', 'failed'
])
```

## API Endpoints mới

### 1. Theo dõi đơn hàng cho Customer

#### Lấy thông tin theo dõi một đơn hàng
```http
GET /orders/{order_id}/tracking/?customer_id={customer_id}
```

**Response:**
```json
{
    "id": 1,
    "total_amount": "99.99",
    "payment_method": "credit_card",
    "shipping_method": "standard",
    "payment_status": "paid",
    "shipping_status": "shipped",
    "status": "shipped",
    "shipping_address": "123 Main St",
    "approval_status": "approved",
    "tracking_number": "TRK001",
    "estimated_delivery": "2026-03-22T10:00:00Z",
    "created_at": "2026-03-19T08:00:00Z",
    "updated_at": "2026-03-19T10:00:00Z",
    "items": [...]
}
```

#### Lấy tất cả đơn hàng của customer
```http
GET /customers/{customer_id}/orders/
```

### 2. Duyệt đơn hàng cho Staff

#### Lấy danh sách đơn hàng chờ duyệt
```http
GET /orders/pending/
```

**Response:**
```json
[
    {
        "id": 1,
        "customer_id": 123,
        "total_amount": "99.99",
        "approval_status": "pending",
        "created_at": "2026-03-19T08:00:00Z",
        "items": [...]
    }
]
```

#### Lấy chi tiết đơn hàng để duyệt
```http
GET /orders/{order_id}/approval/
```

#### Duyệt đơn hàng
```http
POST /orders/{order_id}/approval/
Content-Type: application/json

{
    "action": "approve",
    "staff_id": 1,
    "tracking_number": "TRK001",
    "estimated_delivery": "2026-03-22T10:00:00Z",
    "notes": "Đơn hàng đã được duyệt"
}
```

#### Từ chối đơn hàng
```http
POST /orders/{order_id}/approval/
Content-Type: application/json

{
    "action": "reject",
    "staff_id": 1,
    "rejection_reason": "Sản phẩm tạm hết hàng"
}
```

#### Cập nhật thông tin theo dõi
```http
PATCH /orders/{order_id}/approval/
Content-Type: application/json

{
    "status": "shipped",
    "tracking_number": "TRK002",
    "notes": "Đã giao cho đơn vị vận chuyển"
}
```

## Quy trình hoạt động

### 1. Quy trình duyệt đơn hàng
1. Customer tạo đơn hàng → `approval_status = "pending"`
2. Staff xem danh sách đơn hàng chờ duyệt
3. Staff duyệt/từ chối đơn hàng
4. Nếu duyệt: `approval_status = "approved"`, `status = "processing"`
5. Nếu từ chối: `approval_status = "rejected"`, `status = "cancelled"`, hoàn trả stock

### 2. Quy trình theo dõi đơn hàng
1. Customer tra cứu đơn hàng bằng order_id + customer_id
2. Xem thông tin: trạng thái, tracking number, ngày giao dự kiến
3. Staff cập nhật trạng thái theo tiến độ xử lý

## Trạng thái đơn hàng

### Approval Status
- `pending`: Chờ duyệt
- `approved`: Đã duyệt
- `rejected`: Đã từ chối

### Order Status
- `pending`: Chờ xử lý
- `processing`: Đang xử lý
- `confirmed`: Đã xác nhận
- `shipped`: Đã giao vận
- `delivered`: Đã giao hàng
- `cancelled`: Đã hủy
- `failed`: Thất bại

## Bảo mật

- Customer chỉ có thể xem đơn hàng của chính mình (kiểm tra customer_id)
- Staff có thể xem và duyệt tất cả đơn hàng
- Cần implement authentication/authorization trong production

## Testing

Sử dụng file `test_order_apis.py` để test các API:

```bash
python test_order_apis.py
```

## Migration

Database đã được cập nhật với migration `0003_order_tracking_approval.py`:

```bash
docker-compose run --rm order-service python manage.py migrate
```

## Tích hợp với Frontend

### Cho Customer (API Gateway)
- Thêm trang theo dõi đơn hàng
- Hiển thị trạng thái và thông tin vận chuyển
- Lịch sử đơn hàng

### Cho Staff (Admin Panel)
- Dashboard đơn hàng chờ duyệt
- Form duyệt/từ chối đơn hàng
- Cập nhật trạng thái vận chuyển

## Lưu ý

1. **Stock Management**: Khi từ chối đơn hàng, hệ thống tự động hoàn trả stock
2. **Timestamps**: Tự động ghi nhận thời gian duyệt/từ chối
3. **Validation**: Kiểm tra quyền truy cập và trạng thái hợp lệ
4. **Error Handling**: Xử lý lỗi và trả về thông báo phù hợp

## Mở rộng tương lai

- Thông báo email/SMS khi trạng thái thay đổi
- Tích hợp với API vận chuyển thực tế
- Dashboard analytics cho staff
- Export báo cáo đơn hàng