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
    echo ""
    # 启动后台同步任务
    python manage.py updatecatalog > /tmp/catalog-sync.log 2>&1 &
    echo "同步任务已启动，日志: /tmp/catalog-sync.log"
    echo ""
fi

echo "=== 启动 Gunicorn ==="
exec gunicorn gutendex.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3
