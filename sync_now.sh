#!/bin/bash
# 立即同步数据的脚本
# 使用方法：在 Zeabur 命令终端运行: bash sync_now.sh

set -e

echo "=========================================="
echo "开始同步 Project Gutenberg 数据"
echo "=========================================="
echo ""
echo "⚠️  注意："
echo "   - 同步过程可能需要 30-60 分钟"
echo "   - 会下载约 200-300MB 的数据"
echo "   - 同步过程中服务可能会变慢"
echo ""
echo "正在启动同步..."
echo ""

# 运行数据库迁移（如果需要）
echo "1. 运行数据库迁移..."
python manage.py migrate --noinput

# 开始同步数据
echo "2. 开始同步数据..."
echo "   这可能需要较长时间，请耐心等待..."
echo ""

python manage.py updatecatalog

echo ""
echo "=========================================="
echo "✅ 数据同步完成！"
echo "=========================================="
echo ""
echo "现在可以访问 /books 端点查看同步的数据了"

