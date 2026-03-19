from django.core.management.base import BaseCommand
from app.models import Book


class Command(BaseCommand):
    help = 'Seed database with sample books'

    SAMPLE_BOOKS = [
        {
            "title": "Dạy Con Yêu Thương",
            "author": "Như Hương",
            "price": 189000,
            "stock": 50,
            "image_url": "https://images-na.ssl-images-amazon.com/images/P/B08K2XZPPZ.01.L.jpg"
        },
        {
            "title": "Tâm Lý Học Tối Giản",
            "author": "Sabaa Tahir",
            "price": 220000,
            "stock": 35,
            "image_url": "https://images-na.ssl-images-amazon.com/images/P/B071L7QG8X.01.L.jpg"
        },
        {
            "title": "Thói Quen Nguyên Tử",
            "author": "James Clear",
            "price": 198000,
            "stock": 60,
            "image_url": "https://images-na.ssl-images-amazon.com/images/P/0735211299.01.L.jpg"
        },
        {
            "title": "Sống Là Để Yêu",
            "author": "Nguyên Hà",
            "price": 145000,
            "stock": 45,
            "image_url": "https://images-na.ssl-images-amazon.com/images/P/B08MY32NPR.01.L.jpg"
        },
        {
            "title": "Khí Chất Con Người",
            "author": "Tường Vân",
            "price": 175000,
            "stock": 40,
            "image_url": "https://images-na.ssl-images-amazon.com/images/P/B07ZPFQVLC.01.L.jpg"
        },
        {
            "title": "Cuộc Sống Ý Nghĩa",
            "author": "Viktor Frankl",
            "price": 165000,
            "stock": 55,
            "image_url": "https://images-na.ssl-images-amazon.com/images/P/0807014312.01.L.jpg"
        },
        {
            "title": "Sức Mạnh Của Hiện Tại",
            "author": "Eckhart Tolle",
            "price": 205000,
            "stock": 30,
            "image_url": "https://images-na.ssl-images-amazon.com/images/P/1577314808.01.L.jpg"
        },
        {
            "title": "Tư Duy Nước Ngoài",
            "author": "Thích Nhất Hạnh",
            "price": 155000,
            "stock": 70,
            "image_url": "https://images-na.ssl-images-amazon.com/images/P/B00YG2U8UQ.01.L.jpg"
        },
        {
            "title": "Biến Bạn Thành Nhân Vật",
            "author": "Robin Sharma",
            "price": 189000,
            "stock": 42,
            "image_url": "https://images-na.ssl-images-amazon.com/images/P/1401952216.01.L.jpg"
        },
        {
            "title": "Trí Tuệ Cảm Xúc",
            "author": "Daniel Goleman",
            "price": 210000,
            "stock": 38,
            "image_url": "https://images-na.ssl-images-amazon.com/images/P/055338371X.01.L.jpg"
        }
    ]

    def handle(self, *args, **options):
        """Chạy seed command"""
        self.stdout.write(self.style.SUCCESS('🌱 Bắt đầu thêm dữ liệu sách mẫu...'))
        
        created_count = 0
        for book_data in self.SAMPLE_BOOKS:
            # Kiểm tra sách đã tồn tại chưa
            if not Book.objects.filter(title=book_data['title']).exists():
                book = Book.objects.create(**book_data)
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ Thêm: {book.title} (ID: {book.id})")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"  ⊘ Đã tồn tại: {book_data['title']}")
                )
        
        total = Book.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f'\n✨ Hoàn thành! Đã thêm {created_count} cuốn sách mới.')
        )
        self.stdout.write(
            self.style.SUCCESS(f'📚 Tổng số sách: {total}')
        )
