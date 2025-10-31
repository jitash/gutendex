#!/bin/bash
set -e

echo "=== 运行数据库迁移 ==="
python manage.py migrate --noinput

# 检查数据库是否为空，如果为空则启动后台同步
BOOK_COUNT=$(python manage.py shell -c "
from books.models import Book
try:
    print(Book.objects.count())
except:
    print('0')
" 2>/dev/null || echo "0")

if [ "$BOOK_COUNT" = "0" ]; then
    echo ""
    echo "⚠️  检测到数据库为空"
    echo "📚 正在后台启动数据同步..."
    echo "⏰ 同步可能需要 30-60 分钟，数据会在后台自动导入"
    echo "📝 你可以通过日志查看同步进度"
    echo ""
    # 启动后台同步任务（使用 nohup 和 & 确保在后台运行）
    (nohup python manage.py updatecatalog > /tmp/catalog-sync.log 2>&1 &)
    echo "✅ 同步任务已在后台启动"
    echo ""
fi

# 启动定时数据同步调度器（如果启用）
AUTO_SYNC_ENABLED=${AUTO_SYNC_ENABLED:-true}
if [ "$AUTO_SYNC_ENABLED" = "true" ]; then
    echo "=== 启动定时数据同步调度器 ==="
    echo "📅 已启用自动数据同步"
    echo "⏰ 默认每天自动同步一次（可通过 AUTO_SYNC_TIME 和 AUTO_SYNC_SCHEDULE 环境变量配置）"
    # 在后台启动调度器
    (nohup python manage.py start_scheduler > /tmp/scheduler.log 2>&1 &)
    echo "✅ 定时同步调度器已启动"
    echo ""
fi

echo "=== 启动 Gunicorn ==="
exec gunicorn gutendex.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3
