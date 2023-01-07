from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Book(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=255, blank=True)
    discount = models.IntegerField(null=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                              related_name='my_books')

    readers = models.ManyToManyField(User, through='UserBookRelational',
                                     related_name='books')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=None, null=True)

    def __str__(self):
        return f"Id: {self.pk}, name: {self.name}"


class UserBookRelational(models.Model):
    RateChoices = (
        (1, 'ok'),
        (2, 'good'),
        (3, 'well'),
        (4, 'very well'),
        (5, 'excellent')
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    rate = models.PositiveIntegerField(choices=RateChoices, null=True,
                                       validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self):
        return f"Id {self.pk}: Book - {self.book.name}: rate - {self.get_rate_display()}"

    def save(self, *args, **kwargs):
        from store.logic import get_book_rate
        super().save(*args, **kwargs)
        get_book_rate(self.book)

