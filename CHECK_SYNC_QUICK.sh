#!/bin/bash
# 快速检查同步状态的脚本

echo "=========================================="
echo "快速检查同步状态"
echo "=========================================="
echo ""

# 1. 检查同步进程
echo "1. 检查同步进程..."
SYNC_PID=$(ps aux | grep -E "updatecatalog|python.*manage.py.*updatecatalog" | grep -v grep | awk '{print $2}')
if [ -z "$SYNC_PID" ]; then
    echo "   ⚠️  同步进程未运行"
else
    echo "   ✅ 同步进程正在运行 (PID: $SYNC_PID)"
fi
echo ""

# 2. 检查数据库书籍数量
echo "2. 检查数据库状态..."
python manage.py shell -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gutendex.settings')
import django
django.setup()
from books.models import Book
try:
    count = Book.objects.count()
    print(f'   📚 数据库中的书籍数量: {count}')
    if count > 0:
        print('   ✅ 数据库有数据，同步已成功！')
    else:
        print('   ⚠️  数据库为空，需要同步')
except Exception as e:
    print(f'   ❌ 无法访问数据库: {e}')
" 2>/dev/null || echo "   ❌ 无法检查数据库"
echo ""

# 3. 检查日志文件
echo "3. 检查日志文件..."
if [ -f "/tmp/catalog-sync.log" ]; then
    echo "   ✅ 日志文件存在"
    echo "   最后 5 行日志："
    tail -n 5 /tmp/catalog-sync.log
    if grep -q "Done!" /tmp/catalog-sync.log 2>/dev/null; then
        echo ""
        echo "   ✅ 日志显示同步已完成"
    fi
else
    echo "   ⚠️  日志文件不存在（可能是：还未启动、在另一个容器中、或容器重启了）"
fi
echo ""

# 4. 总结和建议
echo "=========================================="
echo "总结"
echo "=========================================="

DB_COUNT=$(python manage.py shell -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gutendex.settings'); import django; django.setup(); from books.models import Book; print(Book.objects.count())" 2>/dev/null)

if [ ! -z "$DB_COUNT" ] && [ "$DB_COUNT" -gt 0 ]; then
    echo "✅ 同步已成功！数据库中有 $DB_COUNT 本书"
    echo ""
    echo "验证方法：访问 API 端点查看书籍列表"
elif [ ! -z "$SYNC_PID" ]; then
    echo "⏳ 同步正在进行中（进程 PID: $SYNC_PID）"
    echo ""
    echo "建议："
    echo "1. 等待同步完成（可能需要 30-60 分钟）"
    echo "2. 查看日志: tail -f /tmp/catalog-sync.log（如果文件存在）"
    echo "3. 定期检查数据库: python manage.py shell -c \"from books.models import Book; print(Book.objects.count())\""
else
    echo "❌ 同步未运行"
    echo ""
    echo "建议："
    echo "1. 启动同步: nohup python manage.py updatecatalog > /tmp/catalog-sync.log 2>&1 &"
    echo "2. 查看日志: tail -f /tmp/catalog-sync.log"
fi

