@echo off
cd "c:\Disk D\SA&D\bt05-nhom\Bookstore\book-service\book_service"
echo [*] Running migrations...
python manage.py migrate
echo.
echo [*] Seeding books...
python manage.py seed_books
echo.
echo Done!
pause
