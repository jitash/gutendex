from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
from django.conf import settings
import threading
import json


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

