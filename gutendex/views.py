from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
from django.conf import settings
import threading
import json
import os
import logging
import requests
from functools import wraps
import time

logger = logging.getLogger(__name__)


@csrf_exempt
def trigger_sync(request):
    """
    通过 HTTP 请求触发数据同步
    访问: POST /trigger-sync
    需要设置 SECRET_TOKEN 环境变量作为验证
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    # 验证 token（简单验证，生产环境建议使用更安全的方式）
    token = request.POST.get('token') or request.GET.get('token')
    secret_token = getattr(settings, 'SYNC_SECRET_TOKEN', 'change-me')
    
    if token != secret_token:
        return JsonResponse({'error': 'Invalid token'}, status=403)
    
    # 在后台线程中运行同步
    def run_sync():
        try:
            call_command('updatecatalog')
        except Exception as e:
            print(f'Sync error: {str(e)}')
    
    thread = threading.Thread(target=run_sync, daemon=True)
    thread.start()
    
    return JsonResponse({
        'status': 'started',
        'message': 'Catalog sync started in background. This may take 30-60 minutes.'
    })


# 代理功能配置
GUTENDEX_API_URL = os.environ.get('GUTENDEX_API_URL', 'https://gutendex.com')
MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 100 * 1024 * 1024))  # 100MB
REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', 30))  # 30秒


def log_request(f):
    """请求日志装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # request 是函数的第一个参数
        request = args[0] if args else None
        start_time = time.time()
        if request:
            logger.info(f"📥 请求: {request.method} {request.path}")
        try:
            result = f(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"✅ 响应时间: {duration:.2f}秒")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"❌ 错误 (耗时: {duration:.2f}秒): {str(e)}")
            raise
    return decorated_function


@csrf_exempt
def health_check(request):
    """健康检查端点"""
    return JsonResponse({
        "status": "ok",
        "service": "gutendex-proxy",
        "version": "1.0.0"
    })


@csrf_exempt
@log_request
def get_book_info(request, book_id):
    """获取书籍信息（不下载文件）"""
    try:
        book_id = int(book_id)
    except ValueError:
        return JsonResponse({'error': 'Invalid book ID'}, status=400)
    
    # 从 Gutendex API 获取书籍信息
    api_url = f"{GUTENDEX_API_URL}/books/{book_id}/"
    
    try:
        response = requests.get(api_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return JsonResponse(response.json())
    except requests.exceptions.RequestException as e:
        logger.error(f"获取书籍信息失败: {str(e)}")
        return JsonResponse({'error': f'Failed to fetch book info: {str(e)}'}, status=500)

