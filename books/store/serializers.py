from rest_framework import serializers

from store.models import Book, UserBookRelational


class BookSerializer(serializers.ModelSerializer):
    like_method = serializers.SerializerMethodField()
    like_annotate = serializers.IntegerField(read_only=True)
    rate_annotate = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    discount_annotate = serializers.IntegerField(read_only=True)

    class Meta:
        model = Book
        fields = ('id', 'name', 'price', 'author_name', 'like_method',
                  'like_annotate', 'rate_annotate', 'discount_annotate')

    def get_like_method(self, instance):
        return UserBookRelational.objects.filter(book=instance, like=True).count()


class UserBookRelationalSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBookRelational
        fields = ('book', 'like', 'in_bookmarks', 'rate')
