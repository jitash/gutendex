# 数据同步指南

Gutendex 需要从 Project Gutenberg 同步书籍数据才能正常工作。

## 方法 1: 通过 Zeabur 命令终端（推荐）

1. 在 Zeabur 控制台中，打开 gutendex 服务
2. 点击 "命令" 标签
3. 依次运行以下命令：

```bash
# 1. 运行数据库迁移（如果还没运行）
python manage.py migrate

# 2. 开始数据同步（这会下载和处理整个 Project Gutenberg 目录，可能需要 30-60 分钟）
python manage.py updatecatalog
```

## 方法 2: 通过启动脚本自动同步

启动脚本会自动运行迁移。数据同步需要手动触发。

## 注意事项

- `updatecatalog` 命令会：
  - 下载 Project Gutenberg 的 RDF 文件压缩包（约 200-300MB）
  - 解压缩文件
  - 解析所有书籍信息并导入数据库
  - 整个过程可能需要 30-60 分钟或更长时间
  
- 确保 Zeabur 服务有足够的存储空间（建议至少 1GB）
- 同步过程中服务可能会变慢，这是正常的
- 首次同步后，之后只需要定期同步更新即可

## 验证数据

同步完成后，访问 `https://gutendex.zeabur.app/books` 应该能看到书籍数据。

