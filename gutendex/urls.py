from django.urls import include, re_path
from django.views.generic import TemplateView

from rest_framework import routers

from books import views
from gutendex import views as gutendex_views


router = routers.DefaultRouter()
router.register(r'books', views.BookViewSet)

urlpatterns = [
    re_path(r'^$', TemplateView.as_view(template_name='home.html')),
    re_path(r'^trigger-sync', gutendex_views.trigger_sync, name='trigger-sync'),
    re_path(r'^proxy/(?P<book_id>\d+)/(?P<format_str>[^/]+)/?$', views.proxy_file, name='proxy-file'),
    re_path(r'^', include(router.urls)),
]
