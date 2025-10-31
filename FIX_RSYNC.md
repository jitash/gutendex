# 修复 rsync 问题

## 问题描述

在 Zeabur 容器环境中运行数据同步时，出现错误：
```
Error: [Errno 2] No such file or directory: 'rsync'
```

这是因为容器环境中没有安装 `rsync` 命令。

## 解决方案

已将 `updatecatalog.py` 中的 `rsync` 命令替换为纯 Python 实现：

- **新增 `sync_directories()` 函数**：使用 `shutil` 模块实现目录同步
- **功能完全兼容**：实现与 rsync 相同的功能
  - 同步源目录到目标目录
  - 删除目标目录中不存在的文件（`--delete-after`）
  - 递归复制目录和文件
- **添加错误处理**：如果同步失败，会使用后备方案继续执行

## 已修复

✅ 不再依赖外部 `rsync` 命令  
✅ 使用纯 Python 标准库实现  
✅ 兼容所有容器环境  
✅ 保持原有功能不变  

## 重新部署

修复后需要重新部署服务：

1. 代码已自动推送到 GitHub
2. 在 Zeabur 上重新部署服务
3. 重新运行同步命令：

```bash
nohup python manage.py updatecatalog > /tmp/catalog-sync.log 2>&1 &
```

## 验证

同步应该可以正常完成，不会再出现 rsync 相关的错误。

