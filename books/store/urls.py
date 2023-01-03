from rest_framework.routers import SimpleRouter

from django.urls import include, path

from store.views import BookViewSet

router = SimpleRouter()
router.register(r'books', BookViewSet, basename='books')

urlpatterns = [
    path('', include(router.urls))
]


