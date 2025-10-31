"""
简化的数据同步命令
可以通过 HTTP API 触发，避免长时间占用终端
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
import subprocess
import threading


class Command(BaseCommand):
    help = 'Start catalog sync in background'

    def handle(self, *args, **options):
        self.stdout.write('Starting catalog sync in background...')
        self.stdout.write('This will download and process the entire Project Gutenberg catalog.')
        self.stdout.write('This process may take 30-60 minutes or more.')
        self.stdout.write('You can monitor progress in the logs.')
        
        # 在后台线程中运行 updatecatalog
        def run_sync():
            try:
                call_command('updatecatalog')
                self.stdout.write(self.style.SUCCESS('Catalog sync completed successfully!'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Catalog sync failed: {str(e)}'))
        
        thread = threading.Thread(target=run_sync, daemon=True)
        thread.start()
        
        self.stdout.write('Catalog sync started in background. Check logs for progress.')

