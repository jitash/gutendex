#!/bin/bash
# 检查同步状态的脚本
# 使用方法：在 Zeabur 终端运行: bash CHECK_SYNC_STATUS.sh

echo "=========================================="
echo "检查同步状态"
echo "=========================================="
echo ""

# 1. 检查同步进程是否还在运行
echo "1. 检查同步进程..."
SYNC_PID=$(ps aux | grep -E "updatecatalog|python.*manage.py.*updatecatalog" | grep -v grep | awk '{print $2}')
if [ -z "$SYNC_PID" ]; then
    echo "   ✅ 同步进程未运行（可能已完成或未启动）"
else
    echo "   ⏳ 同步进程正在运行 (PID: $SYNC_PID)"
fi
echo ""

# 2. 检查日志文件
echo "2. 检查同步日志..."
if [ -f "/tmp/catalog-sync.log" ]; then
    LOG_SIZE=$(stat -c%s /tmp/catalog-sync.log 2>/dev/null || stat -f%z /tmp/catalog-sync.log 2>/dev/null)
    echo "   📝 日志文件大小: $LOG_SIZE bytes"
    
    # 检查是否显示 "Done!"
    if grep -q "Done!" /tmp/catalog-sync.log 2>/dev/null; then
        echo "   ✅ 日志显示同步已完成"
    else
        echo "   ⏳ 日志显示同步仍在进行中"
    fi
    
    echo ""
    echo "   最后 10 行日志："
    tail -n 10 /tmp/catalog-sync.log
else
    echo "   ⚠️  日志文件不存在"
fi
echo ""

# 3. 检查数据库中的书籍数量
echo "3. 检查数据库状态..."
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
        print('   ✅ 数据库有数据')
    else:
        print('   ⚠️  数据库为空')
except Exception as e:
    print(f'   ❌ 无法访问数据库: {e}')
" 2>/dev/null || echo "   ❌ 无法检查数据库"
echo ""

# 4. 检查同步任务调度器
echo "4. 检查同步调度器..."
SCHEDULER_PID=$(ps aux | grep "start_scheduler" | grep -v grep | awk '{print $2}')
if [ -z "$SCHEDULER_PID" ]; then
    echo "   ℹ️  调度器未运行"
else
    echo "   ✅ 调度器正在运行 (PID: $SCHEDULER_PID)"
fi
echo ""

# 5. 总结
echo "=========================================="
echo "总结"
echo "=========================================="

# 检查是否完成
if [ -f "/tmp/catalog-sync.log" ] && grep -q "Done!" /tmp/catalog-sync.log 2>/dev/null; then
    echo "✅ 同步已完成！"
    echo ""
    echo "验证方法："
    echo "1. 访问 API: https://your-gutendex-url.zeabur.app/books"
    echo "2. 应该能看到书籍列表"
elif [ ! -z "$SYNC_PID" ]; then
    echo "⏳ 同步仍在进行中..."
    echo ""
    echo "查看实时日志: tail -f /tmp/catalog-sync.log"
else
    echo "❓ 无法确定同步状态"
    echo ""
    echo "建议："
    echo "1. 查看完整日志: cat /tmp/catalog-sync.log"
    echo "2. 检查数据库: python manage.py shell -c \"from books.models import Book; print(Book.objects.count())\""
fi

