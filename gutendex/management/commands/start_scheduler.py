"""
启动定时数据同步调度器的管理命令
这个命令应该作为独立的进程运行，在后台启动调度器
"""
from django.core.management.base import BaseCommand
from gutendex.scheduler import start_scheduler
import time
import signal
import sys


class Command(BaseCommand):
    help = 'Start the automatic catalog sync scheduler'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('正在启动定时数据同步调度器...'))
        
        # 启动调度器
        start_scheduler()
        
        # 注册信号处理器，优雅关闭
        def signal_handler(sig, frame):
            self.stdout.write(self.style.WARNING('\n正在关闭调度器...'))
            from gutendex.scheduler import stop_scheduler
            stop_scheduler()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        self.stdout.write(self.style.SUCCESS('定时数据同步调度器已启动，正在运行中...'))
        
        # 保持进程运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            signal_handler(None, None)

