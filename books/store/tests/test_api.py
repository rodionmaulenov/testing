import json

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Case, When, Avg, Sum, F
from django.urls import reverse

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelational
from store.serializers import BookSerializer


class ApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='user1')
        self.user2 = User.objects.create(username='user2')
        self.user4 = User.objects.create(username='user4')
        self.user_staff = User.objects.create(username='staff', is_staff=True)

        self.book = Book.objects.create(name='Test book 1', price='25.00', author_name='Rodion', owner=self.user)
        self.book1 = Book.objects.create(name='Test book 2', price=55, author_name='Rodion')
        self.book2 = Book.objects.create(name='Test 3', price=75, author_name='Rodion')

        UserBookRelational.objects.create(book=self.book, user=self.user, like=True, rate=4)
        UserBookRelational.objects.create(book=self.book, user=self.user2, like=True, rate=3)
        UserBookRelational.objects.create(book=self.book, user=self.user4, like=False, rate=2)

        self.books = Book.objects.all().annotate(
            like_annotate=Count(Case(When(userbookrelational__like=True, then=1))),
            rate_annotate=Avg('userbookrelational__rate'),
            discount_annotate=Sum((F('price') * F('discount')) / 100)
        ).order_by('id')

    def test_get_list(self):
        url = reverse('books-list')
        response = self.client.get(url)
        serializer_data = BookSerializer(self.books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    # def test_get_filter(self):
    #     url = reverse('books-list')
    #     response = self.client.get(url, data={'price': 25})
    #     serializer_data = BookSerializer([self.book], many=True).data
    #     # self.assertEqual(status.HTTP_200_OK, response.status_code)
    #     print(serializer_data)
    #     print(response.data)
    #     # self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('books-list')
        books = Book.objects.filter(id__in=[self.book.id, self.book1.id]).annotate(
            like_annotate=Count(Case(When(userbookrelational__like=True, then=1))),
            rate_annotate=Avg('userbookrelational__rate'),
            discount_annotate=Sum((F('price') * F('discount')) / 100)
        ).order_by('id')
        response = self.client.get(url, data={'search': 'book'})
        serializer_data = BookSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        books = Book.objects.filter(id__in=[self.book.id, self.book1.id, self.book2.id]).annotate(
            like_annotate=Count(Case(When(userbookrelational__like=True, then=1))),
            rate_annotate=Avg('userbookrelational__rate'),
            discount_annotate=Sum((F('price') * F('discount')) / 100)
        ).order_by('id')
        url = reverse('books-list')
        response = self.client.get(url, data={'ordering': 'price'})
        serializer_data = BookSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_minus_ordering(self):
        books = Book.objects.filter(id__in=[self.book.id, self.book1.id, self.book2.id]).annotate(
            like_annotate=Count(Case(When(userbookrelational__like=True, then=1))),
            rate_annotate=Avg('userbookrelational__rate'),
            discount_annotate=Sum((F('price') * F('discount')) / 100)
        ).order_by('-id')
        url = reverse('books-list')
        response = self.client.get(url, data={'ordering': '-price'})
        serializer_data = BookSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        self.assertEqual(Book.objects.count(), 3)
        self.client.force_login(self.user)
        url = reverse('books-list')
        data = {
            'name': 'Popka',
            'price': 500,
            'author_name': 'Plov',
        }
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(Book.objects.count(), 4)
        self.assertEqual('500.00', response.data['price'])

    def test_update(self):
        self.assertEqual('Test book 1', self.book.name)
        self.client.force_login(self.user)
        url = reverse('books-detail', args=(self.book.pk,))
        data = {
            'name': 'Popka',
            'price': 500,
            'author_name': 'Plov'
        }
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')
        book_obj = self.book
        book_obj.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('Popka', response.data['name'])

    def test_get_detail(self):
        d = BookSerializer(self.books, many=True).data
        url = reverse('books-detail', args=(self.book.pk,))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(d[0], response.data)

    def test_not_create(self):
        user = User.objects.create(username='Popanegra4')
        self.client.force_login(user)
        url = reverse('books-list')
        data = {
            'price': 500,
        }
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual({'name': [ErrorDetail(string='This field is required.', code='required')]},
                         response.data)

    def test_delete(self):
        self.assertEqual(Book.objects.count(), 3)
        self.client.force_login(self.user)
        url = reverse('books-detail', kwargs={'pk': self.book.id})
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(Book.objects.count(), 2)

        with self.assertRaises(ObjectDoesNotExist) as cm:
            Book.objects.get(name='Test book 1')
        the_exception = cm.exception
        self.assertEqual('Book matching query does not exist.', the_exception.args[0])

    def test_update_not_owner(self):
        user = User.objects.create(username='user3')
        self.assertEqual('Test book 1', self.book.name)
        self.client.force_login(user)
        url = reverse('books-detail', args=(self.book.pk,))
        data = {
            'name': 'Popka',
            'price': 500,
            'author_name': 'Plov'
        }
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')
        book_obj = self.book
        book_obj.refresh_from_db()
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual('Test book 1', self.book.name)
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')}, response.data)

    def test_update_is_staff(self):
        self.assertEqual('Test book 1', self.book.name)
        self.client.force_login(self.user_staff)
        url = reverse('books-detail', args=(self.book.pk,))
        data = {
            'name': 'Popka',
            'price': 500,
            'author_name': 'Plov'
        }
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data, content_type='application/json')
        book_obj = self.book
        book_obj.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('Popka', self.book.name)

    def test_not_owner_delete(self):
        self.assertEqual(3, Book.objects.count())
        user = User.objects.create(username='Kairat')
        self.client.force_login(user)
        url = reverse('books-detail', kwargs={'pk': self.book.id})
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(3, Book.objects.count())
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')}, response.data)

    def test_book_contains_like(self):
        book = self.books.get(id=1)
        serializer_data = BookSerializer(book).data
        url = reverse('books-detail', args=(self.book.pk,))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(serializer_data.get('like_method'), 2)
        self.assertEqual(serializer_data.get('like_annotate'), 2)
        self.assertEqual(serializer_data.get('rate_annotate'), '3.00')


class UserBookRelationalTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='user1')
        self.user2 = User.objects.create(username='user2')
        self.book = Book.objects.create(name='Test book 1', price='25.00', author_name='Rodion',
                                        owner=self.user)
        self.book1 = Book.objects.create(name='Test book 2', price=55, author_name='Rodion',
                                         owner=self.user2)

    def test_update_field(self):
        self.client.force_login(self.user)
        url = reverse('books_relation-detail', args=(self.book.pk,))
        data = {
            'like': True,
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelational.objects.get(user=self.user, book=self.book)
        self.assertTrue(relation.like)

        url = reverse('books_relation-detail', args=(self.book.pk,))
        data = {
            'in_bookmarks': True,
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelational.objects.get(user=self.user, book=self.book)
        self.assertTrue(relation.in_bookmarks)

    def test_choices(self):
        self.client.force_login(self.user)
        url = reverse('books_relation-detail', args=(self.book.pk,))
        data = {
            'rate': 2,
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelational.objects.get(user=self.user, book=self.book)
        self.assertEqual(2, relation.rate)

    def test_bad_choices(self):
        self.client.force_login(self.user)
        url = reverse('books_relation-detail', args=(self.book.pk,))
        data = {
            'rate': 6,
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual({'rate': [ErrorDetail(string='"6" is not a valid choice.', code='invalid_choice')]},
                         response.data)
