from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg, Sum, F
from django.test import TestCase

from store.models import Book, UserBookRelational
from store.serializers import BookSerializer, UserBookRelationalSerializer


class BookSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='Kairat')
        self.book = Book.objects.create(name='Test book 1', price=25, author_name='Rodion', owner=self.user,
                                        discount=10)
        self.book1 = Book.objects.create(name='Test book 2', price=55, author_name='Rodion1', owner=self.user)

        UserBookRelational.objects.create(book=self.book, user=self.user, like=True, rate=4)
        UserBookRelational.objects.create(book=self.book1, user=self.user, like=True, rate=2)

    def test_book_serializer(self):
        self.book.readers.add(self.user)
        self.book1.readers.add(self.user)
        books = Book.objects.all().annotate(
            like_annotate=Count(Case(When(userbookrelational__like=True, then=1))),
            rate_annotate=Avg('userbookrelational__rate'),
            discount_annotate=Sum((F('price') * F('discount')) / 100)
        ).order_by('id')
        serializer_data = BookSerializer(books, many=True).data
        expected_data = [
            {
                'id': self.book.id,
                'name': 'Test book 1',
                'price': '25.00',
                'author_name': 'Rodion',
                'like_method': 1,
                'like_annotate': 1,
                'rate_annotate': '4.00',
                'discount_annotate': 2
            },
            {
                'id': self.book1.id,
                'name': 'Test book 2',
                'price': '55.00',
                'author_name': 'Rodion1',
                'like_method': 1,
                'like_annotate': 1,
                'rate_annotate': '2.00',
                'discount_annotate': None
            }
        ]

        self.assertEqual(serializer_data, expected_data)


class UserBookRelationalSerializerTestCase(TestCase):
    def setUp(self) -> None:
        self.user = self.user = User.objects.create(username='user1')
        self.book = Book.objects.create(name='Test book 1', price=25, author_name='Rodion', owner=self.user)
        self.user_book = UserBookRelational.objects.create(user=self.user, book=self.book)

    def test_user_book_related_serializer(self):
        serializer_data = UserBookRelationalSerializer(self.user_book).data
        expected_data = {
            'book': self.book.pk,
            'like': False,
            'in_bookmarks': False,
            'rate': None
        }
        self.assertEqual(expected_data, serializer_data)
        self.assertFalse(expected_data.get('like'))
