from django.contrib import admin
from django.contrib.admin import ModelAdmin

from store.models import Book, UserBookRelational


@admin.register(Book)
class BookAdmin(ModelAdmin):
    pass


@admin.register(UserBookRelational)
class UserBookRelationalAdmin(ModelAdmin):
    pass
