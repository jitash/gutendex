# 自动数据同步功能实现说明

## 概述

已为 gutendex 项目实现自动数据同步功能，部署后会自动定期从 Project Gutenberg 同步书籍数据。

## 实现内容

### 1. 新增文件

- `gutendex/scheduler.py` - 定时任务调度器模块
- `gutendex/management/commands/start_scheduler.py` - 管理命令用于启动调度器
- `gutendex/management/__init__.py` - 管理模块初始化
- `gutendex/management/commands/__init__.py` - 命令模块初始化

### 2. 修改文件

- `requirements.txt` - 添加 `apscheduler>=3.10.4` 依赖
- `start.sh` - 在启动脚本中添加自动启动定时调度器的逻辑
- `gutendex/wsgi.py` - 更新注释说明
- `SYNC_DATA.md` - 更新文档说明自动同步功能

## 核心功能

### 自动同步
- **默认启用**：部署后自动启用
- **默认频率**：每天凌晨 2:00 (UTC) 自动同步一次
- **防重复执行**：确保同一时间只有一个同步任务运行
- **日志记录**：同步过程记录到 `/tmp/scheduler.log`

### 环境变量配置

可以通过 Zeabur 环境变量自定义同步行为：

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

## 工作流程

1. **启动时检查**：`start.sh` 在启动时检查 `AUTO_SYNC_ENABLED` 环境变量
2. **启动调度器**：如果启用，在后台启动 `python manage.py start_scheduler`
3. **定时执行**：调度器根据配置的时间定期执行 `updatecatalog` 命令
4. **同步数据**：从 Project Gutenberg 下载并处理最新数据

## 技术实现

### 使用 APScheduler
- 使用 `BackgroundScheduler` 作为后台调度器
- 使用 `CronTrigger` 实现基于 cron 表达式的定时任务
- 支持灵活的配置选项

### 进程管理
- 调度器作为独立进程运行，不影响主 Web 服务
- 使用 `nohup` 确保后台运行
- 支持优雅关闭（SIGTERM/SIGINT）

### 错误处理
- 同步任务失败不会影响调度器继续运行
- 错误信息记录到日志文件
- 支持异常捕获和记录

## 部署说明

### 在 Zeabur 上部署

1. **推送代码**：确保最新代码已推送到 GitHub
2. **重新部署**：在 Zeabur 上触发重新部署
3. **配置环境变量**（可选）：
   ```
   AUTO_SYNC_ENABLED=true
   AUTO_SYNC_TIME=02:00
   AUTO_SYNC_SCHEDULE=daily
   ```
4. **验证部署**：查看日志确认调度器已启动

### 验证自动同步

1. **查看调度器日志**：
   ```bash
   tail -f /tmp/scheduler.log
   ```

2. **查看同步任务日志**：
   ```bash
   tail -f /tmp/catalog-sync.log
   ```

3. **手动触发测试**（如果需要）：
   ```bash
   python manage.py updatecatalog
   ```

## 注意事项

- 首次同步可能需要 30-60 分钟
- 确保服务器有足够的存储空间（建议至少 1GB）
- 同步过程中服务可能会变慢，这是正常的
- 建议在流量较低的时段进行同步（默认凌晨 2 点）

## 后续优化建议

1. 添加同步进度监控 API
2. 添加同步通知（邮件/Webhook）
3. 支持增量同步优化
4. 添加同步历史记录

## 相关文档

- 详细使用说明：`SYNC_DATA.md`
- 安装指南：`https://github.com/garethbjohnson/gutendex/wiki/Installation-Guide`

