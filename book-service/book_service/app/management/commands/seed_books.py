from django.core.management.base import BaseCommand
from app.models import Book


class Command(BaseCommand):
    help = 'Seed database with sample books'

    SAMPLE_BOOKS = [
    {
        "title": "Dạy Con Yêu Thương",
        "author": "Như Hương",
        "price": "189000",
        "stock": 50,
        "image_url": "https://plus.unsplash.com/premium_photo-1773711129295-942f5ed7c014?q=80&w=717&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    },
    {
        "title": "Tâm Lý Học Tối Giản",
        "author": "Sabaa Tahir",
        "price": "220000",
        "stock": 35,
        "image_url": "https://plus.unsplash.com/premium_photo-1673290748844-126a4f1a60dd?q=80&w=765&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    },
    {
        "title": "Thói Quen Nguyên Tử",
        "author": "James Clear",
        "price": "198000",
        "stock": 60,
        "image_url": "https://images-na.ssl-images-amazon.com/images/P/0735211299.01.L.jpg"
    },
    {
        "title": "Sống Là Để Yêu",
        "author": "Nguyên Hà",
        "price": "145000",
        "stock": 45,
        "image_url": "https://images.unsplash.com/photo-1711185901036-f7fd98e50bb1?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    },
    {
        "title": "Khí Chất Con Người",
        "author": "Tường Vân",
        "price": "175000",
        "stock": 40,
        "image_url": "https://images.unsplash.com/photo-1600714226481-1f78bae21075?q=80&w=736&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    },
    {
        "title": "Cuộc Sống Ý Nghĩa",
        "author": "Viktor Frankl",
        "price": "165000",
        "stock": 55,
        "image_url": "https://images.unsplash.com/photo-1594370606841-a3da498dcec8?q=80&w=1074&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    },
    {
        "title": "Sức Mạnh Của Hiện Tại",
        "author": "Eckhart Tolle",
        "price": "205000",
        "stock": 30,
        "image_url": "https://images-na.ssl-images-amazon.com/images/P/1577314808.01.L.jpg"
    },
    {
        "title": "Tư Duy Nước Ngoài",
        "author": "Thích Nhất Hạnh",
        "price": "155000",
        "stock": 70,
        "image_url": "https://images.unsplash.com/photo-1667964395070-2dd7bd81d914?q=80&w=687&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    },
    {
        "title": "Biến Bạn Thành Nhân Vật",
        "author": "Robin Sharma",
        "price": "189000",
        "stock": 42,
        "image_url": "https://images-na.ssl-images-amazon.com/images/P/1401952216.01.L.jpg"
    },
    {
        "title": "Trí Tuệ Cảm Xúc",
        "author": "Daniel Goleman",
        "price": "210000",
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
