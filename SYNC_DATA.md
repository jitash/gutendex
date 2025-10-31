# 数据同步指南

Gutendex 需要从 Project Gutenberg 同步书籍数据才能正常工作。

## 自动同步（推荐）

**部署后会自动启用定时数据同步功能！**

### 默认配置
- **启用状态**：默认启用（可通过环境变量 `AUTO_SYNC_ENABLED=false` 禁用）
- **同步频率**：每天一次
- **同步时间**：每天凌晨 2:00（UTC）

### 自定义配置

在 Zeabur 环境变量中设置以下变量来自定义同步行为：

#### `AUTO_SYNC_ENABLED`
- **默认值**：`true`
- **说明**：是否启用自动同步
- **示例**：`AUTO_SYNC_ENABLED=false` 禁用自动同步

#### `AUTO_SYNC_TIME`
- **默认值**：`02:00`
- **说明**：每天同步的时间（24小时制，UTC时区）
- **示例**：`AUTO_SYNC_TIME=03:00` 设置为凌晨 3 点

#### `AUTO_SYNC_SCHEDULE`
- **默认值**：`daily`
- **说明**：同步频率
- **可选值**：
  - `daily` - 每天同步（默认）
  - `weekly` - 每周一同步
  - `cron:0 2 * * *` - 自定义 cron 表达式（格式：`cron:分钟 小时 日 月 星期`）
    - 例如：`cron:0 2 * * *` 每天凌晨 2 点
    - 例如：`cron:0 0 * * 1` 每周一午夜

### 示例配置

在 Zeabur 设置以下环境变量：
```
AUTO_SYNC_ENABLED=true
AUTO_SYNC_TIME=02:00
AUTO_SYNC_SCHEDULE=daily
```

## 手动同步

如果需要立即同步数据或自动同步被禁用，可以手动触发同步：

### 方法 1: 通过 Zeabur 命令终端

1. 在 Zeabur 控制台中，打开 gutendex 服务
2. 点击 "命令" 标签
3. 运行以下命令：

```bash
# 开始数据同步（这会下载和处理整个 Project Gutenberg 目录，可能需要 30-60 分钟）
python manage.py updatecatalog
```

### 方法 2: 通过启动脚本

首次部署时，如果数据库为空，启动脚本会自动触发一次数据同步。

## 注意事项

- `updatecatalog` 命令会：
  - 下载 Project Gutenberg 的 RDF 文件压缩包（约 200-300MB）
  - 解压缩文件
  - 解析所有书籍信息并导入数据库
  - 整个过程可能需要 30-60 分钟或更长时间
  
- 确保 Zeabur 服务有足够的存储空间（建议至少 1GB）
- 同步过程中服务可能会变慢，这是正常的
- 首次同步后，自动同步会定期更新数据

## 验证数据

同步完成后，访问 `https://gutendex.zeabur.app/books` 应该能看到书籍数据。

## 查看同步日志

- **自动同步日志**：`/tmp/scheduler.log`
- **手动同步日志**：`/tmp/catalog-sync.log`

可以通过 Zeabur 的命令终端查看日志：

```bash
# 查看调度器日志
tail -f /tmp/scheduler.log

# 查看同步任务日志
tail -f /tmp/catalog-sync.log
```

