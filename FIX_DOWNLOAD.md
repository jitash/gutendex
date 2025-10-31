# 修复下载问题

## 问题描述

在下载 Project Gutenberg RDF 文件时，遇到网络中断错误：
```
Error: <urlopen error retrieval incomplete: got only 169284 out of 124477158 bytes>
```

这是因为下载大文件（约 118MB）时网络连接不稳定，导致下载不完整。

## 解决方案

已添加下载重试机制和文件完整性验证：

### 新增功能

1. **自动重试机制**
   - 最多重试 5 次
   - 每次重试间隔 10 秒
   - 自动清理不完整的下载文件

2. **文件完整性验证**
   - 验证下载文件大小（应该大于 100MB）
   - 如果文件太小，自动删除并重试
   - 确保下载完整

3. **错误处理**
   - 捕获网络错误（URLError, IOError, OSError）
   - 详细的错误日志
   - 友好的错误提示

4. **进度日志**
   - 显示下载尝试次数
   - 显示下载文件大小
   - 显示重试倒计时

## 使用说明

修复后，同步命令会自动处理网络中断：

1. **自动重试**
   - 如果下载失败，会自动重试
   - 最多尝试 5 次
   - 每次重试前等待 10 秒

2. **查看进度**
   ```bash
   tail -f /tmp/catalog-sync.log
   ```
   你会看到类似这样的日志：
   ```
   Downloading compressed catalog...
     Attempt 1/5...
     Download completed: 118.64 MB
   ```

3. **如果网络仍然不稳定**
   - 可以多次运行同步命令
   - 每次运行都会自动重试
   - 已经下载的文件会被清理后重新下载

## 重新运行同步

修复后，可以重新运行同步命令：

```bash
# 重新启动同步
nohup python manage.py updatecatalog > /tmp/catalog-sync.log 2>&1 &

# 查看进度
tail -f /tmp/catalog-sync.log
```

## 注意事项

- 下载 118MB 文件需要稳定网络连接
- 如果网络不稳定，可能需要多次重试
- 重试间隔为 10 秒，避免频繁请求
- 确保有足够的存储空间（至少 500MB）

## 验证

同步成功后，日志会显示：
```
Download completed: 118.64 MB
Decompressing catalog...
...
Done!
```

