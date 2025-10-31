# 快速同步数据指南

## 🚀 立即同步数据（Zeabur 终端）

如果部署后数据没有自动同步，可以在 Zeabur 命令终端中执行：

```bash
# 方法 1: 后台运行（推荐）
nohup python manage.py updatecatalog > /tmp/catalog-sync.log 2>&1 &

# 方法 2: 使用同步脚本
bash sync_now.sh

# 查看同步进度
tail -f /tmp/catalog-sync.log
```

## 📋 详细步骤

1. **打开 Zeabur 控制台**
   - 访问 https://zeabur.com
   - 登录并找到 `gutendex` 项目

2. **打开服务终端**
   - 点击服务 → "Terminal" 或 "命令" 标签

3. **执行同步命令**
   ```bash
   nohup python manage.py updatecatalog > /tmp/catalog-sync.log 2>&1 &
   ```

4. **查看同步进度**
   ```bash
   tail -f /tmp/catalog-sync.log
   ```

5. **验证同步结果**
   - 等待同步完成（约 30-60 分钟）
   - 访问 `https://your-gutendex-url.zeabur.app/books`
   - 应该能看到书籍列表

## ⚠️ 注意事项

- 同步过程可能需要 30-60 分钟
- 会下载约 200-300MB 的数据
- 同步期间服务可能会变慢（正常现象）
- 建议在流量较低时段进行同步

## 🔍 检查同步状态

```bash
# 查看同步进程
ps aux | grep updatecatalog

# 查看日志文件大小（如果一直在增长，说明正在同步）
ls -lh /tmp/catalog-sync.log

# 检查数据库中的书籍数量
python manage.py shell -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gutendex.settings')
import django
django.setup()
from books.models import Book
print('书籍总数:', Book.objects.count())
"
```

## 📚 更多信息

详细说明请查看 `MANUAL_SYNC.md`

