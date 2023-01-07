from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Sum, F, Prefetch
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from store.models import Book, UserBookRelational
from store.permissions import IsOwnerOrIsStaffOrReadOnly
from store.serializers import BookSerializer, UserBookRelationalSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all().defer(
        'owner__is_superuser',
        'owner__password',
        'owner__last_login',
        'owner__email',
        'owner__is_staff',
        'owner__is_active',
        'owner__date_joined'
    ).annotate(
        like_annotate=Count(Case(When(userbookrelational__like=True, then=1))),
        discount_annotate=Sum((F('price') * F('discount')) / 100),
    ).select_related('owner').prefetch_related(
        Prefetch('readers', queryset=User.objects.only('first_name', 'last_name'))
    ).order_by('id')
    serializer_class = BookSerializer
    permission_classes = [IsOwnerOrIsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filter_fields = ['price']
    search_fields = ['name', 'author_name']
    ordering_fields = ['price', 'author_name']

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class UserBookRelationalView(UpdateModelMixin,
                             GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserBookRelational
    serializer_class = UserBookRelationalSerializer
    lookup_field = 'book'

    def get_object(self, *args, **kwargs):
        obj, _ = UserBookRelational.objects.get_or_create(user=self.request.user,
                                                          book_id=self.kwargs.get('book'))
        return obj


def auth(request):
    return render(request, 'oauth.html')
