# Docker Development Guide

## Tổng quan

Đã cập nhật Docker Compose để hỗ trợ development với tính năng auto-reload và volume mounting.

## Các file Docker Compose

### 1. `docker-compose.yml` (Production)
- Cấu hình cơ bản cho production
- Có volumes để mount code
- Environment variables cơ bản

### 2. `docker-compose.dev.yml` (Development)
- Tối ưu cho development
- Auto-reload khi code thay đổi
- DEBUG=True
- restart: unless-stopped

## Cách sử dụng

### Sử dụng Makefile (Khuyến nghị)

```bash
# Xem tất cả lệnh có sẵn
make help

# Khởi động development environment
make dev

# Xem logs của tất cả services
make dev-logs

# Xem logs của service cụ thể
make logs-order-service

# Chạy migration cho tất cả services
make migrate

# Chạy migration cho service cụ thể
make migrate-order-service

# Mở shell trong service
make shell-order-service

# Kiểm tra health của tất cả services
make health

# Dừng tất cả services
make down

# Dọn dẹp containers và images
make clean
```

### Sử dụng Docker Compose trực tiếp

```bash
# Development mode (auto-reload)
docker-compose -f docker-compose.dev.yml up -d

# Production mode
docker-compose up -d

# Xem logs
docker-compose logs -f order-service

# Chạy migration
docker-compose run --rm order-service python manage.py migrate

# Mở shell
docker-compose exec order-service bash

# Dừng services
docker-compose down
```

## Tính năng Auto-reload

### Cách hoạt động
- Code từ host được mount vào container qua volumes
- Django runserver tự động detect thay đổi file
- Container restart khi có lỗi fatal

### Các thư mục được mount
```yaml
volumes:
  - ./order-service/order_service:/app  # Mount source code
```

### Environment variables
```yaml
environment:
  - DJANGO_SETTINGS_MODULE=order_service.settings
  - PYTHONPATH=/app
  - DEBUG=True  # Chỉ trong dev mode
```

## Workflow Development

### 1. Khởi động development environment
```bash
make dev
```

### 2. Kiểm tra services đã chạy
```bash
make health
```

### 3. Xem logs khi develop
```bash
make logs-order-service
```

### 4. Chỉnh sửa code
- Sửa file trong thư mục local
- Container tự động reload
- Xem kết quả ngay lập tức

### 5. Chạy migration khi cần
```bash
make migrate-order-service
```

### 6. Debug trong container
```bash
make shell-order-service
```

## Port Mapping

| Service | Port | URL |
|---------|------|-----|
| API Gateway | 8000 | http://localhost:8000 |
| Customer Service | 8001 | http://localhost:8001 |
| Book Service | 8002 | http://localhost:8002 |
| Cart Service | 8003 | http://localhost:8003 |
| Staff Service | 8004 | http://localhost:8004 |
| Manager Service | 8005 | http://localhost:8005 |
| Catalog Service | 8006 | http://localhost:8006 |
| Order Service | 8007 | http://localhost:8007 |
| Ship Service | 8008 | http://localhost:8008 |
| Pay Service | 8009 | http://localhost:8009 |
| Comment Rate Service | 8010 | http://localhost:8010 |
| Recommend AI Service | 8011 | http://localhost:8011 |

## Troubleshooting

### Container không start
```bash
# Xem logs để debug
make logs-order-service

# Rebuild image
make build

# Restart service
docker-compose restart order-service
```

### Code không auto-reload
```bash
# Kiểm tra volume mount
docker-compose exec order-service ls -la /app

# Restart container
docker-compose restart order-service
```

### Migration lỗi
```bash
# Chạy migration thủ công
make shell-order-service
python manage.py migrate --fake-initial
```

### Port conflict
```bash
# Kiểm tra port đang sử dụng
netstat -tulpn | grep :8007

# Thay đổi port trong docker-compose.yml
ports:
  - "8017:8000"  # Thay vì 8007:8000
```

## Best Practices

### 1. Development
- Luôn sử dụng `make dev` cho development
- Commit code thường xuyên
- Test API sau mỗi thay đổi

### 2. Database
- Backup database trước khi chạy migration
- Sử dụng migration files thay vì thay đổi trực tiếp

### 3. Logs
- Monitor logs khi develop: `make dev-logs`
- Sử dụng log levels phù hợp

### 4. Performance
- Chỉ chạy services cần thiết
- Dọn dẹp containers định kỳ: `make clean`

## Ví dụ Workflow

```bash
# 1. Khởi động development
make dev

# 2. Kiểm tra health
make health

# 3. Develop tính năng mới trong order-service
# Sửa file order-service/order_service/app/views.py

# 4. Xem logs để debug
make logs-order-service

# 5. Test API
curl http://localhost:8007/orders/pending/

# 6. Tạo migration nếu cần
make shell-order-service
python manage.py makemigrations
python manage.py migrate

# 7. Commit code
git add .
git commit -m "Add new feature"

# 8. Dừng services khi xong
make down
```

## Lưu ý

1. **File permissions**: Đảm bảo user có quyền read/write trên thư mục project
2. **Docker version**: Sử dụng Docker Compose v3.8+
3. **Memory**: Đảm bảo đủ RAM cho tất cả containers
4. **Network**: Các services giao tiếp qua Docker network internal