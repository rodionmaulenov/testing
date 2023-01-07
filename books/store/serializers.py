from django.contrib.auth.models import User

from rest_framework import serializers

from store.models import Book, UserBookRelational


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class BookSerializer(serializers.ModelSerializer):
    like_annotate = serializers.IntegerField(read_only=True)
    discount_annotate = serializers.IntegerField(read_only=True)
    user_name = serializers.CharField(source='owner.username', default='',
                                      read_only=True)
    user_inf = UserSerializer(many=True, read_only=True, source='readers')

    class Meta:
        model = Book
        fields = ('id', 'name', 'price', 'author_name',
                  'like_annotate', 'discount_annotate',
                  'user_name', 'user_inf', 'rating')


class UserBookRelationalSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBookRelational
        fields = ('book', 'like', 'in_bookmarks', 'rate')
