import urllib.parse
import urllib.request

from django.db.models import Q
from django.http import StreamingHttpResponse, Http404

from rest_framework import exceptions as drf_exceptions, viewsets

from .models import *
from .serializers import *


class BookViewSet(viewsets.ModelViewSet):
    """ This is an API endpoint that allows books to be viewed. """

    lookup_field = 'gutenberg_id'

    queryset = Book.objects.exclude(download_count__isnull=True)
    queryset = queryset.exclude(title__isnull=True)

    serializer_class = BookSerializer

    def get_queryset(self):
        queryset = self.queryset

        sort = self.request.GET.get('sort')
        if sort == 'ascending':
            queryset = queryset.order_by('id')
        elif sort == 'descending':
            queryset = queryset.order_by('-id')
        else:
            queryset = queryset.order_by('-download_count')

        author_year_end = self.request.GET.get('author_year_end')
        try:
            author_year_end = int(author_year_end)
        except:
            author_year_end = None
        if author_year_end is not None:
            queryset = queryset.filter(
                Q(authors__birth_year__lte=author_year_end) |
                Q(authors__death_year__lte=author_year_end)
            )

        author_year_start = self.request.GET.get('author_year_start')
        try:
            author_year_start = int(author_year_start)
        except:
            author_year_start = None
        if author_year_start is not None:
            queryset = queryset.filter(
                Q(authors__birth_year__gte=author_year_start) |
                Q(authors__death_year__gte=author_year_start)
            )

        copyright_parameter = self.request.GET.get('copyright')
        if copyright_parameter is not None:
            copyright_strings = copyright_parameter.split(',')
            copyright_values = set()
            for copyright_string in copyright_strings:
                if copyright_string == 'true':
                    copyright_values.add(True)
                elif copyright_string == 'false':
                    copyright_values.add(False)
                elif copyright_string == 'null':
                    copyright_values.add(None)
            for value in [True, False, None]:
                if value not in copyright_values:
                    queryset = queryset.exclude(copyright=value)

        id_string = self.request.GET.get('ids')
        if id_string is not None:
            ids = id_string.split(',')

            try:
                ids = [int(id) for id in ids]
            except ValueError:
                pass
            else:
                queryset = queryset.filter(gutenberg_id__in=ids)

        language_string = self.request.GET.get('languages')
        if language_string is not None:
            language_codes = [code.lower() for code in language_string.split(',')]
            queryset = queryset.filter(languages__code__in=language_codes)

        mime_type = self.request.GET.get('mime_type')
        if mime_type is not None:
            queryset = queryset.filter(format__mime_type__startswith=mime_type)

        search_string = self.request.GET.get('search')
        if search_string is not None:
            search_terms = search_string.split(' ')
            for term in search_terms[:32]:
                queryset = queryset.filter(
                    Q(authors__name__icontains=term) | Q(title__icontains=term)
                )

        topic = self.request.GET.get('topic')
        if topic is not None:
            queryset = queryset.filter(
                Q(bookshelves__name__icontains=topic) | Q(subjects__name__icontains=topic)
            )

        return queryset.distinct()


def proxy_file(request, book_id, format_str):
    """
    代理从 gutenberg.org 下载文件
    URL 格式: /proxy/{bookId}/{format}
    format 可以是:
    - MIME type 的 URL 编码版本，如 "text%2Fplain" (对应 "text/plain")
    - 简化的格式标识，如 "plain", "html", "epub" 等
    """
    try:
        book_id = int(book_id)
    except ValueError:
        raise Http404("Invalid book ID")

    # 查找书籍
    try:
        book = Book.objects.get(gutenberg_id=book_id)
    except Book.DoesNotExist:
        raise Http404("Book not found")

    # 解码格式参数（URL 解码）
    decoded_format = urllib.parse.unquote(format_str)

    # 查找匹配的格式
    # 先尝试精确匹配 MIME type
    formats = Format.objects.filter(book=book, mime_type=decoded_format)

    # 如果没有精确匹配，尝试通过格式后缀匹配（如 "plain" 匹配 "text/plain"）
    if not formats.exists():
        formats = Format.objects.filter(
            book=book,
            mime_type__contains=decoded_format
        )

    # 如果还是没有匹配，尝试通过常见格式标识匹配
    format_mappings = {
        'plain': 'text/plain',
        'html': 'text/html',
        'epub': 'application/epub+zip',
        'kindle': 'application/x-mobipocket-ebook',
        'pdf': 'application/pdf',
    }
    if not formats.exists() and decoded_format.lower() in format_mappings:
        formats = Format.objects.filter(
            book=book,
            mime_type=format_mappings[decoded_format.lower()]
        )

    if not formats.exists():
        raise Http404("Format not found for this book")

    # 使用第一个匹配的格式
    format_obj = formats.first()
    source_url = format_obj.url

    # 如果 URL 是相对路径，需要拼接 gutenberg.org 的域名
    if not source_url.startswith('http'):
        if source_url.startswith('/'):
            source_url = f"https://www.gutenberg.org{source_url}"
        else:
            source_url = f"https://www.gutenberg.org/{source_url}"

    try:
        # 从源服务器下载文件
        req = urllib.request.Request(source_url)
        req.add_header('User-Agent', 'Gutendex-Proxy/1.0')
        
        response = urllib.request.urlopen(req, timeout=30)
        
        # 获取响应头信息
        content_type = response.headers.get('Content-Type', format_obj.mime_type)
        content_length = response.headers.get('Content-Length')
        
        # 创建流式读取文件的生成器函数
        def file_iterator(response, chunk_size=8192):
            try:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
            finally:
                response.close()

        # 创建流式响应
        http_response = StreamingHttpResponse(
            file_iterator(response),
            content_type=content_type
        )
        
        # 设置响应头
        if content_length:
            http_response['Content-Length'] = content_length
        http_response['Content-Disposition'] = f'inline; filename="book-{book_id}.{decoded_format.split("/")[-1]}"'
        http_response['X-Proxy-Source'] = 'gutendex'
        http_response['Cache-Control'] = 'public, max-age=3600'
        
        return http_response

    except urllib.error.HTTPError as e:
        raise Http404(f"Failed to fetch file from source: {e.code}")
    except urllib.error.URLError as e:
        raise Http404(f"Network error: {str(e)}")
    except Exception as e:
        raise Http404(f"Error downloading file: {str(e)}")
