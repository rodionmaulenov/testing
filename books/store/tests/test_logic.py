from django.test import TestCase

from django.contrib.auth.models import User

from store.logic import get_book_rate
from store.models import Book, UserBookRelational


class LogicTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user', first_name='Rodion', last_name='Maulenov')
        self.user2 = User.objects.create(username='user1', first_name='Natalia', last_name='Maulenov')
        self.user3 = User.objects.create(username='user2', first_name='Timur', last_name='Maulenov')

        self.book = Book.objects.create(name='Test book 1', price=25, author_name='Rodion', owner=self.user,
                                        discount=10)
        self.book1 = Book.objects.create(name='Test book 2', price=55, author_name='Rodion1', owner=self.user2)

        UserBookRelational.objects.create(book=self.book, user=self.user, like=True, rate=4)
        UserBookRelational.objects.create(book=self.book, user=self.user3, like=True, rate=4)
        UserBookRelational.objects.create(book=self.book1, user=self.user2, like=True, rate=2)

    def test_not_new_instance(self):
        self.book.refresh_from_db()
        self.assertEqual('4.00', str(self.book.rating))

    def test_not_equal_rating_book(self):
        UserBookRelational.objects.create(book=self.book, user=self.user2, like=True, rate=5)

        get_book_rate(self.book)
        self.book.refresh_from_db()
        self.assertEqual('4.33', str(self.book.rating))

    def test_get_book_rate(self):
        user = User.objects.create(username='popka', first_name='Rodion', last_name='Maulenov')

        book = Book.objects.create(name='Test book 1', price=25, author_name='Rodion', owner=user,
                                   discount=10)

        user_book = UserBookRelational.objects.create(book=book, user=user, like=True)

        get_book_rate(book)
        book.refresh_from_db()
        self.assertEqual(None, book.rating)

        user_book.rate = 4
        user_book.save()
        get_book_rate(book)
        book.refresh_from_db()
        self.assertEqual('4.00', str(book.rating))
