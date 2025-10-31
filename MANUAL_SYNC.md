# 手动同步数据指南

如果部署后数据没有自动同步，可以按照以下方法手动触发同步。

## 方法 1: 通过 Zeabur 命令终端同步（推荐）

### 步骤：

1. **登录 Zeabur 控制台**
   - 访问 https://zeabur.com
   - 登录你的账户

2. **进入服务**
   - 找到 `gutendex` 项目
   - 点击进入服务页面

3. **打开命令终端**
   - 点击顶部的 "Terminal" 或 "命令" 标签
   - 这会打开一个可以执行命令的终端

4. **运行同步命令**
   在终端中执行以下命令：

```bash
# 方法 1: 直接运行同步命令（会阻塞终端，但可以看到实时进度）
python manage.py updatecatalog

# 方法 2: 后台运行（推荐，不会阻塞终端）
nohup python manage.py updatecatalog > /tmp/catalog-sync.log 2>&1 &
```

### 查看同步进度

如果使用后台运行，可以通过以下命令查看日志：

```bash
# 实时查看日志
tail -f /tmp/catalog-sync.log

# 查看最后 50 行日志
tail -n 50 /tmp/catalog-sync.log

# 查看日志文件大小（判断是否在下载数据）
ls -lh /tmp/catalog-sync.log
```

## 方法 2: 使用同步脚本

1. **上传同步脚本**（如果项目中没有）
   - 项目已包含 `sync_now.sh` 脚本

2. **在 Zeabur 终端执行**
```bash
bash sync_now.sh
```

## 方法 3: 检查自动同步是否正常

如果应该自动同步但没有同步，检查以下内容：

### 1. 检查调度器是否运行

```bash
# 检查调度器进程
ps aux | grep start_scheduler

# 查看调度器日志
tail -f /tmp/scheduler.log
```

### 2. 检查环境变量

确保以下环境变量已设置：

```bash
# 检查环境变量
echo $AUTO_SYNC_ENABLED
echo $AUTO_SYNC_TIME
echo $AUTO_SYNC_SCHEDULE
```

如果 `AUTO_SYNC_ENABLED` 不是 `true`，自动同步可能被禁用。

### 3. 手动启动调度器

如果调度器没有运行，可以手动启动：

```bash
# 后台启动调度器
nohup python manage.py start_scheduler > /tmp/scheduler.log 2>&1 &
```

## 方法 4: 立即触发一次同步（使用调度器命令）

如果你安装了调度器，可以手动触发一次同步：

```bash
# 使用 Python shell 直接调用同步
python manage.py shell -c "
from django.core.management import call_command
call_command('updatecatalog')
"
```

## 验证同步结果

同步完成后，验证数据：

```bash
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

或者在浏览器中访问：
- `https://your-gutendex-url.zeabur.app/books`

如果能看到书籍列表，说明同步成功。

## 常见问题

### Q: 同步过程很慢，正常吗？
A: 正常。首次同步需要：
- 下载约 200-300MB 的 RDF 文件
- 解压缩文件
- 解析和导入所有书籍数据
- 整个过程可能需要 30-60 分钟

### Q: 如何知道同步是否完成？
A: 可以通过以下方式：
- 查看日志文件，看到 "Catalog sync completed" 字样
- 检查进程是否还在运行：`ps aux | grep updatecatalog`
- 查看 API 端点是否有数据返回

### Q: 同步过程中服务无法访问？
A: 正常。同步过程会占用大量资源，可能导致服务暂时变慢。建议：
- 在流量较低的时段进行同步
- 增加服务器资源配置
- 使用后台运行（`nohup ... &`）避免阻塞

### Q: 同步失败怎么办？
A: 
1. 查看错误日志：`cat /tmp/catalog-sync.log`
2. 检查网络连接和存储空间
3. 重试同步命令

## 联系支持

如果以上方法都无法解决问题，可以：
1. 查看详细错误日志
2. 检查 Zeabur 服务日志
3. 联系 Zeabur 技术支持

