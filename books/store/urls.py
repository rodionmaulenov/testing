from rest_framework.routers import SimpleRouter

from django.urls import path, include

from store.views import BookViewSet

router = SimpleRouter()
router.register(r'books', BookViewSet)

urlpatterns = [
]

urlpatterns += router.urls
