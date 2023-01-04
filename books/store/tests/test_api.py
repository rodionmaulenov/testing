import json

from django.contrib.auth.models import User
from django.forms import model_to_dict
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BookSerializer


class ApiTestCase(APITestCase):
    def setUp(self) -> None:
        self.book = Book.objects.create(name='Test book 1', price='25.00', author_name='Rodion')
        self.book1 = Book.objects.create(name='Test book 2', price=55, author_name='Rodion')
        self.book2 = Book.objects.create(name='Test 3', price=75, author_name='Rodion')

    def test_get(self):
        url = reverse('books-list')
        response = self.client.get(url)
        serializer_data = BookSerializer([self.book, self.book1, self.book2], many=True).data
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
        response = self.client.get(url, data={'search': 'book'})
        serializer_data = BookSerializer([self.book, self.book1], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        url = reverse('books-list')
        response = self.client.get(url, data={'ordering': 'price'})
        serializer_data = BookSerializer([self.book, self.book1, self.book2], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_minus_ordering(self):
        url = reverse('books-list')
        response = self.client.get(url, data={'ordering': '-price'})
        serializer_data = BookSerializer([self.book2, self.book1, self.book], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        self.assertEqual(Book.objects.count(), 3)
        user = User.objects.create(username='Popanegra4')
        self.client.force_login(user)
        url = reverse('books-list')
        data = {
            'name': 'Popka',
            'price': 500,
            'author_name': 'Plov'
        }
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(Book.objects.count(), 4)

    def test_update(self):
        self.assertEqual(self.book.name, 'Test book 1')
        user = User.objects.create(username='Popanegra4')
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
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.book.name, response.data['name'])

    def test_get_detail(self):
        url = reverse('books-detail', args=(self.book.pk,))
        response = self.client.get(url)
        d = model_to_dict(self.book)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(d, response.data)

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

    def test_delete(self):
        self.assertEqual(Book.objects.count(), 3)
        user = User.objects.create(username='Kairat')
        self.client.force_login(user)
        url = reverse('books-detail', kwargs={'pk': self.book.id})
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(Book.objects.count(), 2)


