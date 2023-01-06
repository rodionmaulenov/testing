from rest_framework.routers import SimpleRouter

from store.views import BookViewSet, UserBookRelationalView

router = SimpleRouter()
router.register(r'book', BookViewSet, basename='books')
router.register(r'book_relation', UserBookRelationalView, basename='books_relation')

urlpatterns = [
]

urlpatterns += router.urls
