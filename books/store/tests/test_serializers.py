from django.test import TestCase

from store.models import Book
from store.serializers import BookSerializer


class SerializerTestCase(TestCase):
    def test_book_serializer(self):
        book = Book.objects.create(name='Test book 1', price=25, author_name='Rodion')
        book1 = Book.objects.create(name='Test book 2', price=55,  author_name='Rodion1')
        serializer_data = BookSerializer([book, book1], many=True).data
        expected_data = [
            {
                'id': book.id,
                'name': 'Test book 1',
                'price': '25.00',
                'author_name': 'Rodion'
            },
            {
                'id': book1.id,
                'name': 'Test book 2',
                'price': '55.00',
                'author_name': 'Rodion1'
            }
        ]
        self.assertEqual(serializer_data, expected_data)
