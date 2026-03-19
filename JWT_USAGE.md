# JWT Authentication - Hướng Dẫn Sử Dụng

## 📋 Tổng Quan

Hệ thống sử dụng JWT (JSON Web Token) để xác thực người dùng (Customer hoặc Staff) và phân biệt loại người dùng.

---

## 🔐 1. Các Endpoint Login

### API Gateway - Web Form Login
**URL**: `POST http://api-gateway:8000/login/`
- Dùng HTML Form (SessionId)
- Lưu vào Session
- Response: Redirect

### API Gateway - JSON Login (Mobile/Client)
**URL**: `POST http://api-gateway:8000/api/login/`
- Dùng JSON + JWT Token
- Response: JWT Token + User Info

### Customer Service - Direct Login
**URL**: `POST http://customer-service:8000/login/`
- Payload JSON
- Response: JWT Tokens

### Staff Service - Direct Login
**URL**: `POST http://staff-service:8000/login/`
- Payload JSON
- Response: JWT Tokens

---

## 📤 2. Request - Cách Gửi Yêu Cầu Đăng Nhập

### Dùng cURL (API Login)
```bash
curl -X POST http://api-gateway:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "password": "password123"
  }'
```

### Dùng Python requests
```python
import requests
import json

# Customer hoặc Staff đều sử dụng endpoint này
response = requests.post(
    'http://api-gateway:8000/api/login/',
    json={
        'email': 'customer@example.com',
        'password': 'password123'
    }
)

data = response.json()
if data.get('success'):
    user_type = data.get('user_type')  # 'customer' hoặc 'staff'
    tokens = data.get('data')
    access_token = tokens.get('access')
    refresh_token = tokens.get('refresh')
```

### Dùng JavaScript/Fetch
```javascript
const response = await fetch('http://api-gateway:8000/api/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        email: 'customer@example.com',
        password: 'password123'
    })
});

const data = await response.json();
if (data.success) {
    const accessToken = data.data.access;
    const refreshToken = data.data.refresh;
    const userType = data.user_type; // 'customer' hoặc 'staff'
    
    // Lưu tokens vào localStorage
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
    localStorage.setItem('user_type', userType);
}
```

---

## 📥 3. Response - Kết Quả Đăng Nhập

### ✅ Đăng nhập thành công (Customer)
```json
{
    "success": true,
    "user_type": "customer",
    "data": {
        "id": 1,
        "email": "customer@example.com",
        "name": "Nguyễn Văn A",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjQ2Njc3NjAwLCJpYXQiOjE2NDY2NzQwMDAsImp0aSI6ImFiYzEyMyIsImVtYWlsIjoiY3VzdG9tZXJAZXhhbXBsZS5jb20iLCJjdXN0b21lcl9pZCI6MSwidXNlcl90eXBlIjoiY3VzdG9tZXIiLCJuYW1lIjoiTmd1eeG4gVsSBbiBBIn0.xyz...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY0NzI3OTAwMCwiaWF0IjoxNjQ2Njc0MDAwLCJqdGkiOiJkZWYzNDUiLCJlbWFpbCI6ImN1c3RvbWVyQGV4YW1wbGUuY29tIiwiY3VzdG9tZXJfaWQiOjEsInVzZXJfdHlwZSI6ImN1c3RvbWVyIiwibmFtZSI6Ik5ndXvDqm4gVsSBbiBBIn0.abc..."
    }
}
```

### ✅ Đăng nhập thành công (Staff)
```json
{
    "success": true,
    "user_type": "staff",
    "data": {
        "id": 2,
        "email": "staff@example.com",
        "name": "Lê Văn B",
        "role": "manager",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwi...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIs..."
    }
}
```

### ❌ Đăng nhập thất bại
```json
{
    "error": "Invalid password"
}
// Status: 401
```

---

## 🔑 4. Cấu Trúc JWT Token

### Access Token (Payload)
```json
{
    "token_type": "access",
    "exp": 1646677600,
    "iat": 1646674000,
    "jti": "abc123",
    "email": "customer@example.com",
    "customer_id": 1,
    "user_type": "customer",
    "name": "Nguyễn Văn A"
}
```

### Refresh Token (Payload)
```json
{
    "token_type": "refresh",
    "exp": 1647279000,
    "iat": 1646674000,
    "jti": "def456",
    "email": "customer@example.com",
    "customer_id": 1,
    "user_type": "customer",
    "name": "Nguyễn Văn A"
}
```

---

## 📨 5. Sử Dụng Token Trong Requests

### Gửi Token trong Header
```bash
curl -X GET http://customer-service:8000/customers/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Python requests với Token
```python
import requests

access_token = "eyJ0eXAiOiJKV1QiLCJhbGc..."

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

response = requests.get(
    'http://customer-service:8000/customers/',
    headers=headers
)
```

### JavaScript Fetch với Token
```javascript
const accessToken = localStorage.getItem('access_token');

const response = await fetch('http://customer-service:8000/customers/', {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
    }
});
```

---

## ⏰ 6. Token Lifetime

| Token | Lifetime | Mục đích |
|-------|----------|---------|
| **Access Token** | 1 giờ | Xác thực requests |
| **Refresh Token** | 1 ngày | Cấp lại Access Token |

### Refresh Access Token
Khi Access Token hết hạn, dùng Refresh Token để lấy Access Token mới:

```bash
curl -X POST http://customer-service:8000/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

Response:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc... (new token)"
}
```

---

## 🔀 7. Phân Biệt Customer vs Staff

### Cách 1: Dùng `user_type` từ response
```python
data = response.json()
if data.get('user_type') == 'customer':
    print("Đây là Customer")
elif data.get('user_type') == 'staff':
    print("Đây là Staff")
```

### Cách 2: Dùng payload của JWT Token
Decode JWT Token để lấy `user_type`:

```python
import jwt

token = "eyJ0eXAiOiJKV1QiLCJhbGc..."
decoded = jwt.decode(token, options={"verify_signature": False})

user_type = decoded.get('user_type')  # 'customer' hoặc 'staff'
user_id = decoded.get('customer_id') or decoded.get('staff_id')
```

---

## 🛠️ 8. Ví Dụ Hoàn Chỉnh - Login + Gửi Request

### Frontend (JavaScript)
```javascript
// 1. Login
async function login(email, password) {
    const response = await fetch('http://api-gateway:8000/api/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    if (data.success) {
        // Lưu tokens
        localStorage.setItem('access_token', data.data.access);
        localStorage.setItem('refresh_token', data.data.refresh);
        localStorage.setItem('user_type', data.user_type);
        localStorage.setItem('user_id', data.data.id);
        
        console.log(`Đăng nhập thành công! Loại: ${data.user_type}`);
        return true;
    } else {
        console.error(`Lỗi: ${data.error}`);
        return false;
    }
}

// 2. Gửi API request với token
async function makeAuthenticatedRequest(url, method = 'GET', body = null) {
    const accessToken = localStorage.getItem('access_token');
    
    if (!accessToken) {
        console.error('Chưa đăng nhập!');
        return null;
    }
    
    const options = {
        method,
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        }
    };
    
    if (body) options.body = JSON.stringify(body);
    
    let response = await fetch(url, options);
    
    // Nếu token hết hạn (401), refresh và retry
    if (response.status === 401) {
        const refreshed = await refreshAccessToken();
        if (refreshed) {
            const newToken = localStorage.getItem('access_token');
            options.headers['Authorization'] = `Bearer ${newToken}`;
            response = await fetch(url, options);
        }
    }
    
    return response.json();
}

// 3. Refresh token
async function refreshAccessToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    
    const response = await fetch('http://customer-service:8000/token/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken })
    });
    
    if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access);
        return true;
    }
    return false;
}

// Sử dụng:
await login('customer@example.com', 'password123');
const customers = await makeAuthenticatedRequest('http://customer-service:8000/customers/');
```

---

## 🎯 9. Workflow Hoàn Chỉnh

```
┌─────────────────────────────────────────────────────────┐
│ 1. USER SUBMITS LOGIN FORM                              │
│    Email: customer@example.com                          │
│    Password: password123                                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 2. API GATEWAY → POST /api/login/                       │
│    Tries Staff Service first, then Customer Service    │
└────────────────────┬────────────────────────────────────┘
                     │
            ┌────────┴────────┐
            ▼                 ▼
    ┌──────────────┐   ┌──────────────┐
    │ Staff Login  │   │ Customer     │
    │ (Failed)     │   │ Login        │
    └──────────────┘   │ (Success!)   │
                       └──────┬───────┘
                              │
                              ▼
                     ┌─────────────────────┐
                     │ JWT Token Generated │
                     │ - access_token      │
                     │ - refresh_token     │
                     └────────┬────────────┘
                              │
                              ▼
                     ┌─────────────────────┐
                     │ Return JSON         │
                     │ - user_type:        │
                     │   "customer"        │
                     │ - data: {...}       │
                     └────────┬────────────┘
                              │
                              ▼
                     ┌─────────────────────┐
                     │ CLIENT STORES       │
                     │ - access_token      │
                     │ - refresh_token     │
                     │ - user_type         │
                     └─────────────────────┘
```

---

## ✅ 10. Checklist Sử Dụng JWT

- [ ] Login qua `POST /api/login/` để lấy tokens
- [ ] Lưu tokens vào localStorage/sessionStorage
- [ ] Gửi `Authorization: Bearer <token>` trong header
- [ ] Kiểm tra `user_type` trong response để biết là Customer hay Staff
- [ ] Implement token refresh khi access token hết hạn
- [ ] Clear tokens khi logout
- [ ] Xử lý 401 Unauthorized error

---

## 🚀 11. Các Service Hỗ Trợ JWT

| Service | Endpoint | Method |
|---------|----------|--------|
| **Customer Service** | `/login/` | POST |
| **Customer Service** | `/token/refresh/` | POST |
| **Staff Service** | `/login/` | POST |
| **Staff Service** | `/token/refresh/` | POST |
| **API Gateway** | `/api/login/` | POST |

---

## 📌 Notes

- Luôn OTP hoặc xác thực trước khi lưu sensitive data
- JWT được mã hóa nhưng KHÔNG được mã hóa - đừng lưu sensitive info
- Token được gửi trong header, không phải URL parameter
- Luôn sử dụng HTTPS trong production
