"""
定时数据同步任务
使用 APScheduler 实现定期同步 Project Gutenberg 数据
"""
import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management import call_command
from django.conf import settings

logger = logging.getLogger(__name__)

# 调度器实例
_scheduler = None


def sync_catalog_job():
    """定时同步数据任务"""
    try:
        logger.info("开始执行定时数据同步任务...")
        call_command('updatecatalog')
        logger.info("定时数据同步任务完成")
    except Exception as e:
        logger.error(f"定时数据同步任务失败: {str(e)}", exc_info=True)


def start_scheduler():
    """启动定时任务调度器"""
    global _scheduler
    
    # 检查是否启用自动同步
    auto_sync_enabled = os.environ.get('AUTO_SYNC_ENABLED', 'true').lower() == 'true'
    
    if not auto_sync_enabled:
        logger.info("自动同步已禁用（AUTO_SYNC_ENABLED=false）")
        return
    
    if _scheduler and _scheduler.running:
        logger.warning("调度器已在运行，跳过启动")
        return
    
    try:
        _scheduler = BackgroundScheduler()
        
        # 获取同步时间配置，默认为每天凌晨 2 点
        sync_time = os.environ.get('AUTO_SYNC_TIME', '02:00')
        hour, minute = map(int, sync_time.split(':'))
        
        # 获取同步频率，默认每天一次
        sync_schedule = os.environ.get('AUTO_SYNC_SCHEDULE', 'daily')
        
        if sync_schedule == 'daily':
            # 每天指定时间执行
            trigger = CronTrigger(hour=hour, minute=minute)
            logger.info(f"已配置每天 {sync_time} 自动同步数据")
        elif sync_schedule == 'weekly':
            # 每周一执行
            trigger = CronTrigger(day_of_week='mon', hour=hour, minute=minute)
            logger.info(f"已配置每周一 {sync_time} 自动同步数据")
        elif sync_schedule.startswith('cron:'):
            # 自定义 cron 表达式（格式：cron:minute hour day month day_of_week）
            # 例如：cron:0 2 * * * (每天凌晨2点)
            cron_parts = sync_schedule.split(':', 1)[1].strip().split()
            if len(cron_parts) == 5:
                trigger = CronTrigger(
                    minute=cron_parts[0],
                    hour=cron_parts[1],
                    day=cron_parts[2],
                    month=cron_parts[3],
                    day_of_week=cron_parts[4]
                )
                logger.info(f"已配置自定义 cron 表达式自动同步: {sync_schedule}")
            else:
                raise ValueError(f"无效的 cron 表达式: {sync_schedule}")
        else:
            raise ValueError(f"不支持的同步频率: {sync_schedule}")
        
        # 添加定时任务
        _scheduler.add_job(
            sync_catalog_job,
            trigger=trigger,
            id='sync_catalog',
            replace_existing=True,
            max_instances=1  # 确保同一时间只有一个同步任务运行
        )
        
        # 启动调度器
        _scheduler.start()
        logger.info("定时数据同步调度器已启动")
        
    except Exception as e:
        logger.error(f"启动定时数据同步调度器失败: {str(e)}", exc_info=True)
        if _scheduler:
            _scheduler.shutdown()
            _scheduler = None


def stop_scheduler():
    """停止定时任务调度器"""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown()
        logger.info("定时数据同步调度器已停止")
        _scheduler = None

