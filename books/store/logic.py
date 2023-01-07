from django.db.models import Avg

from store.models import UserBookRelational


def get_book_rate(book):
    rating = UserBookRelational.objects.filter(book=book).aggregate(rating=Avg('rate')).get('rating')
    book.rating = rating
    book.save()