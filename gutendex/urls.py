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
    # 健康检查和书籍信息端点（必须在代理文件之前）
    re_path(r'^health$', gutendex_views.health_check, name='health-check'),
    re_path(r'^proxy/info/(?P<book_id>\d+)/?$', gutendex_views.get_book_info, name='proxy-info'),
    # 代理文件端点（使用 books/views.py 中的实现）
    # 注意：必须在 /proxy/info/ 之后，否则 /proxy/info/ 会被匹配
    re_path(r'^proxy/(?P<book_id>\d+)/(?P<format_str>[^/]+)/?$', views.proxy_file, name='proxy-file'),
    # API路由（最后，匹配所有剩余路径）
    re_path(r'^', include(router.urls)),
]
