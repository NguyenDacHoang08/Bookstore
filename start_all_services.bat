@echo off
echo Starting all BookStore microservices...
echo.

REM Start Customer Service
echo [1/11] Starting Customer Service on port 8001...
start "Customer Service" cmd /k "cd customer-service\customer_service && python manage.py runserver 8001"
timeout /t 2 /nobreak >nul

REM Start Book Service
echo [2/11] Starting Book Service on port 8002...
start "Book Service" cmd /k "cd book-service\book_service && python manage.py runserver 8002"
timeout /t 2 /nobreak >nul

REM Start Cart Service
echo [3/11] Starting Cart Service on port 8003...
start "Cart Service" cmd /k "cd cart-service\cart_service && python manage.py runserver 8003"
timeout /t 2 /nobreak >nul

REM Start Staff Service
echo [4/11] Starting Staff Service on port 8004...
start "Staff Service" cmd /k "cd staff-service\staff_service && python manage.py runserver 8004"
timeout /t 2 /nobreak >nul

REM Start Manager Service
echo [5/11] Starting Manager Service on port 8005...
start "Manager Service" cmd /k "cd manager-service\manager_service && python manage.py runserver 8005"
timeout /t 2 /nobreak >nul

REM Start Catalog Service
echo [6/11] Starting Catalog Service on port 8006...
start "Catalog Service" cmd /k "cd catalog-service\catalog_service && python manage.py runserver 8006"
timeout /t 2 /nobreak >nul

REM Start Order Service
echo [7/11] Starting Order Service on port 8007...
start "Order Service" cmd /k "cd order-service\order_service && python manage.py runserver 8007"
timeout /t 2 /nobreak >nul

REM Start Ship Service
echo [8/11] Starting Ship Service on port 8008...
start "Ship Service" cmd /k "cd ship-service\ship_service && python manage.py runserver 8008"
timeout /t 2 /nobreak >nul

REM Start Pay Service
echo [9/11] Starting Pay Service on port 8009...
start "Pay Service" cmd /k "cd pay-service\pay_service && python manage.py runserver 8009"
timeout /t 2 /nobreak >nul

REM Start Comment Rate Service
echo [10/11] Starting Comment Rate Service on port 8010...
start "Comment Rate Service" cmd /k "cd comment-rate-service\comment_rate_service && python manage.py runserver 8010"
timeout /t 2 /nobreak >nul

REM Start Recommend AI Service
echo [11/11] Starting Recommend AI Service on port 8011...
start "Recommend AI Service" cmd /k "cd recommend-ai-service\recommend_ai_service && python manage.py runserver 8011"
timeout /t 2 /nobreak >nul

echo.
echo Waiting for services to start...
timeout /t 5 /nobreak >nul

REM Start API Gateway
echo.
echo Starting API Gateway on port 8000...
start "API Gateway" cmd /k "cd api-gateway && python manage.py runserver 8000"

echo.
echo ========================================
echo All services are starting!
echo ========================================
echo.
echo API Gateway: http://localhost:8000
echo.
echo Press any key to exit this window...
pause >nul
